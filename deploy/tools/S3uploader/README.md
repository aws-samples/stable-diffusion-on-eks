### 文件下载并上传到S3

### 1. 介绍
此工具用于下载文件并上传到到特定S3桶,本地不会保留下载文件

### 2. Requirement

1. python3.8+,argparse,boto3,urllib3,csv
2. 本地临时空间要大于下载文件的大小

### 3. 使用

1. 将profle_name='ue1'修改为自己的配置文件,如果使用Role 认证 使用 s3 = boto3.client('s3')
2. 修改csv文件为需要下载和上传的桶,文件夹可以通过前缀实现,例如下载到桶的123目录,可以直接录入 123/filename
3. 执行 python3 s3uploader.py down.csv即可开始上传

### 4. 注意
代码的逻辑是下载后再上传,并非直接下载到S3,所以下载时间取决于你运行代码的PC/instances的带宽.

