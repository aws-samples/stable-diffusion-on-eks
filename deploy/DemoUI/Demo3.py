import boto3
import gradio as gr
import requests
import json
import time
import logging
import json
import botocore
import traceback


API_URL_INPUT = "https://XXX.execute-api.us-west-2.amazonaws.com/prod/"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(process)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
from botocore.exceptions import ClientError

my_queue = 'output_queue'
# Create an SQS client object
sqs = boto3.client('sqs',region_name="us-west-2")

# Get the queue URL
sqsQueueUrl = sqs.get_queue_url(QueueName=my_queue)['QueueUrl']

sqsRes = boto3.resource('sqs',region_name="us-west-2")
queue = sqsRes.Queue(sqsQueueUrl)

s3 = boto3.client('s3')
start_time = None
end_time = None
total_time = None

with open('./payload1.json', 'r') as p1:
    payload1 = json.load(p1)
    formatted_payload1 = json.dumps(payload1, indent=4)
with open('./payload2.json', 'r') as p2:
    payload2 = json.load(p2)
    formatted_payload2 = json.dumps(payload2, indent=4)
with open('./payload3.json', 'r') as p3:
    payload3 = json.load(p3)
    formatted_payload3 = json.dumps(payload3, indent=4)
with open('./payload4.json', 'r') as p4:
    payload4 = json.load(p4)
    formatted_payload4 = json.dumps(payload4, indent=4)


def choose_option(option):
    if option == "txt2img":
        return formatted_payload1
    elif option == "img2img":
        return formatted_payload2
    elif option == "txt2img with ControlNet":
        return formatted_payload3
    elif option == "txt2img with Lora & ControlNet":
        return formatted_payload4
    else:
        return ""
    
# 生成预签名 URL 的函数
def generate_presigned_url(s3_uri):
    try:
        # 解析 S3 URI 获取桶名和对象键
        s3_uri_parts = s3_uri.replace('s3://', '').split('/')
        bucket_name = s3_uri_parts[0]
        object_key = '/'.join(s3_uri_parts[1:])
        
        # 生成预签名 URL
        presigned_url = s3.generate_presigned_url('get_object',
                                                  Params={'Bucket': bucket_name, 'Key': object_key},
                                                  ExpiresIn=3600)  # 预签名 URL 的有效期（以秒为单位）
        return presigned_url
    except botocore.exceptions.ParamValidationError as e:
        print("生成预签名 URL 时出错：", e)
        return None


def receive_messages(queue, max_number, wait_time):
    """
    Receive a batch of messages in a single request from an SQS queue.

    :param queue: The queue from which to receive messages.
    :param max_number: The maximum number of messages to receive. The actual number
                       of messages received might be less.
    :param wait_time: The maximum time to wait (in seconds) before returning. When
                      this number is greater than zero, long polling is used. This
                      can result in reduced costs and fewer false empty responses.
    :return: The list of Message objects received. These each contain the body
             of the message and metadata and custom attributes.
    """
    try:
        messages = queue.receive_messages(
            MaxNumberOfMessages=max_number,
            WaitTimeSeconds=wait_time,
            AttributeNames=['All'],
            MessageAttributeNames=['All']
        )
    except Exception as error:
        logger.error(f"Error receiving messages: {error}")
    else:
        return messages

def delete_message(message):
    """
    Delete a message from a queue. Clients must delete messages after they
    are received and processed to remove them from the queue.

    :param message: The message to delete. The message's queue URL is contained in
                    the message's metadata.
    :return: None
    """
    try:
        message.delete()
    except ClientError as error:
        traceback.print_exc()
        raise error    
    

def api_request(api_url, json_input):
    global s3prefix
    global start_time
    print ("收到请求,开始计时")
    start_time = time.time()
    #print (json_input)
    try:
        json_data = json.loads(json_input)  # 解析 JSON 数据
        s3prefix = json_data["alwayson_scripts"]["id_task"]
        print ("s3prefix--->",s3prefix)
        response = requests.post(api_url, json=json_data)
        result = json.loads(response.text)
        obj_path  = result["output_location"]
        div = image_gallery(s3prefix)
        #print ("div------>",div)
        return div,obj_path
    except Exception as e:
        return {"error": str(e)}



def image_gallery (task_id):
    global end_time
    global total_time
    while True:
        try:
            received_messages = receive_messages(queue, 1, 20)
            img_urls =[]
            print('received_messages',received_messages)
            for message in received_messages:
                end_time = time.time()
                total_time = end_time - start_time
                print ("任务结束,停止计时,总耗时",total_time,"秒")
                Payload = json.loads(message.body)
                taskid_output = json.loads(Payload['Message'])['parameters']['id_task']
                if int(taskid_output) == int(task_id):
                    print("Processing message with id_task:", taskid_output)
                    url_output = json.loads(Payload['Message'])['parameters']['image_url']
                    url_output_dict = [item.strip('\'') for item in url_output.split(',')]
                    for s3uri in url_output_dict:
                        presigned_url = generate_presigned_url(s3uri)
                        img_urls.append(presigned_url)
                        #print ("presigned_url---->",(presigned_url))
                    #print (taskid_output)
                    print ("图片队列长度--->",len(img_urls))
                delete_message(message)
            #break
        except Exception as e:
            print(e)
            continue
        return (img_urls)


with gr.Blocks(title="SD-on-EKS Demo") as demo:
    gr.Markdown("# Stable diffusion on EKS API Demo")
    with gr.Tab("输入"):
        api_url =gr.Textbox(label="API 请求地址",value=API_URL_INPUT)
        object_path =  gr.Textbox(label="图片生成路径")
        with gr.Row():
            inputs = gr.Radio(["txt2img", "img2img", "txt2img with ControlNet", "txt2img with Lora & ControlNet"], label="选择一个请求")
        with gr.Row():
            payload = gr.Textbox(lines=10,label="Payload输入")
            gallery = gr.Gallery(label="Generated images", show_label=False, elem_id="gallery", columns=[5], rows=[5], object_fit="contain", height=400)
        with gr.Row():
            request_button = gr.Button("提交")
            total_timer =  gr.Textbox(label="图片生成时间(s)",value=total_time)
        inputs.change(fn=choose_option, inputs=inputs, outputs=payload)
    request_button.click(api_request, inputs=[api_url,payload],outputs=[gallery,object_path])
demo.launch()