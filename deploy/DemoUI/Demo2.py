import boto3
import gradio as gr
import requests
import json


# 设置AWS S3的访问密钥和密钥ID
#session = boto3.Session(profile_name='new')
#s3 = session.client('s3')
s3 = boto3.client('s3')
s3bucket =None
s3prefix =None


API_URL_INPUT = "https://XXX.execute-api.us-east-1.amazonaws.com/prod/"

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

# 创建请求 API

def api_request(api_url, json_input):
    global s3prefix
    global s3bucket
    #print (json_input)
    try:
        json_data = json.loads(json_input)  # 解析 JSON 数据
        s3prefix = json_data["alwayson_scripts"]["id_task"]
        #print ("s3prefix--->",s3prefix)
        response = requests.post(api_url, json=json_data)
        result = json.loads(response.text)
        obj_path  = result["output_location"]
        s3bucket = result["output_location"].split('/')[2]
        #print ("s3bucket------>",s3bucket)
        div = image_viewer(s3prefix)
        #print ("div------>",div)
        return div,obj_path
    except Exception as e:
        return {"error": str(e)}


# 获取特定前缀下的所有对象的列表

def list_objects(prefix):
    response = s3.list_objects(Bucket=s3bucket, Prefix=prefix)
    #print (response)
    while "Contents" in response:
        objects = response['Contents']
        return [obj['Key'] for obj in objects]

# 创建图像的HTML标记
def image_viewer(folder):
    image_url = []
    div = ""
    # print ("listobj--->",list_objects(folder))
    # if list_objects(folder) != None :
    #     prev_len = len(list_objects(folder))
    # else :
    #     prev_len = 0
    while True :
        objects = list_objects(folder)
        # cur_len = len(objects)
        # print ("objects ---->",objects)
        # print (prev_len,cur_len)
        while  objects:
            for object_key in objects:
                if object_key.endswith('.jpg') or object_key.endswith('.jpeg') or object_key.endswith('.png'):
                    image_url.append(s3.generate_presigned_url('get_object', Params={
                        'Bucket': s3bucket, 'Key': object_key}, ExpiresIn=3600))
            image_tags = ""
            for image in image_url:
                image_tags += f"<div style='padding: 5px'><a href='{image}' target='_blank'><img src='{image}'></a></div>"
                div = f"<div style='display: grid; grid-template-columns: repeat(5, 1fr); grid-gap: 10px'>{image_tags}</div>"
            return div
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
with gr.Blocks(title="SD-on-EKS Demo") as demo:
    gr.Markdown("# Stable diffusion on EKS API Demo")
    with gr.Tab("输入"):
        api_url =gr.Textbox(label="API 请求地址",value=API_URL_INPUT)
        object_path =  gr.Textbox(label="图片生成路径")
        with gr.Row():
            inputs = gr.Radio(["txt2img", "img2img", "txt2img with ControlNet", "txt2img with Lora & ControlNet"], label="选择一个请求")
        with gr.Row():
            payload = gr.Textbox(lines=10,label="Payload输入")
            picture_output = gr.HTML("图库")
        with gr.Row():
            request_button = gr.Button("提交")
            #total_timer =  gr.Textbox(label="图片生成时间(s)")
        inputs.change(fn=choose_option, inputs=inputs, outputs=payload)
    request_button.click(api_request, inputs=[api_url,payload],outputs=[picture_output,object_path])
demo.launch()
