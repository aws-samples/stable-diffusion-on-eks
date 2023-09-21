import boto3
import gradio as gr
import requests


# 设置AWS S3的访问密钥和密钥ID
#session = boto3.Session(profile_name='ue1')
#s3 = session.client('s3')
s3 = boto3.client('s3')


# 获取特定前缀下的所有对象的列表

def list_objects(Bucket_name,prefix):
    response = s3.list_objects(Bucket=Bucket_name, Prefix=prefix)
    objects = response['Contents']
    return [obj['Key'] for obj in objects]



# 创建图像的HTML标记
def gallery_viewer(Bucket_name,folder):
    objects = list_objects(Bucket_name,folder)
    image_url = []
    for object_key in objects:
        if object_key.endswith('.jpg') or object_key.endswith('.jpeg') or object_key.endswith('.png'):
            image_url.append(s3.generate_presigned_url('get_object', Params={
                'Bucket': Bucket_name, 'Key': object_key}, ExpiresIn=3600))
            #print (image_url)
    return image_url


with gr.Blocks(title="SD-on-EKS Demo") as demo:
    gr.Markdown("# Stable diffusion on EKS API Demo")
    with gr.Tab("输入"):
        with gr.Row():
            Bucket_name = gr.Textbox(label="存储桶名称",value = "sdoneksdataplanestack-outputs3bucket9fe85b9f-pzlnjnu6xsl7")
            folder = gr.Textbox(label="文件夹名称")
            request_button = gr.Button("提交")
        gallery = gr.Gallery(label="Generated images", show_label=False, elem_id="gallery", columns=[5], rows=[5],object_fit="contain", height=400)        
    request_button.click(gallery_viewer, inputs=[Bucket_name,folder],outputs=gallery)
demo.launch(share=True)

