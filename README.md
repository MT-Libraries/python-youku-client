# python-youku-client

python版本优酷客户端 & Gearman Worker

基于Gearman的任务队列Worker,负责接收到任务后下载阿里云OSS文件并上传到使用优酷SDK来上传视频到优酷

## Required

- Gearman
- oss2

```
pip install oss2
pip install gearman
```

## Conf

修改conf目录下的conf_*.sample.py为对应conf_*.py并填写相应参数

- conf/conf_gearman.py
- conf/conf_oss.py
- conf/conf_youku.py

## Usage

- 任务队列

```
python worker.py
```

- 直接上传

```
# 修改client内的参数
python client.py
```

- 任务信息

```
var info = {
    "conf":{
        "clientid" : "0a54dd48sssa79beae8",
        "ak" : "5629915b34ffdsd7eda7fd8747fb712b08e73e8f",
        "keyname": "00d64e1ffdf7701c62b5bffa61ff23303ca5961",
        "callbackurl":"http://your.domain"
    },
    "youku":{
        "title": "优酷合作测试视频",
        "tags": "other",
        "description": "Polymer video #7"
        //"category": "other"         
    }
}
            
client.submitJob("upload", JSON.stringify(info)); 
```

***注意：需要转换JSON为STRING***

- 返回信息

```
{
	"code": "200", 
	"info": "upload success"
 }
 
 # code 200 || 404 || 500  分别对应成功、OSS文件不存在以及优酷上传错误
 # msg 错误信息或者成功信息
```
***注意：返回值为STRING,需要自行处理***

## Reference

Gearman对应的jobServer,worker,client有对应的实现

- [Gearman nodejs on ubuntu](http://blog.thonatos.com/gearman-nodejs-on-ubuntu/)
- [Gearman manual](http://gearman.org/manual/)

## License

The MIT License (MIT)

Copyright (c) 2016 Magic Term Libraries

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.