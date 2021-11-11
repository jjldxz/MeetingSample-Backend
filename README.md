# MeetingSample-Backend

MeetingSample-Backend是在线会议系统的后台服务，是基于大学长开放平台的【互动直播应用】做的二次开发，实现了基本的在线会议的管理系统。

## 准备工作

- 大学长开放平台账户
- 开通【互动直播应用】

账户申请及应用开通请参考官方文档中 [应用注册](https://open.jjldxz.com/zh-hans/resource/document/) 章节。

## 快速开始

### 依赖库安装

项目使用poetry管理Python的依赖库，请先安装poetry。 参考 [poetry的官方文档](https://python-poetry.org/docs)

依赖库的安装可以使用poetry直接安装，也可也使用pip安装。具体如下:

1. 直接使用poetry安装项目依赖

   ```shell script
   poetry install # 安装环境
   poetry shell # 进入虚拟环境
   ```

2. 使用pip安装

   ```shell script
   poetry export -o requirements.txt --without-hashes
   pip install -r requirements.txt
   ```

### 运行环境配置

系统运行需要配置环境变量，方法有两种：

1. 直接设置主机系统的环境变量，如系统为ubuntu，将下列的环境变量写入 ～/.profile文件中
2. 将环境变量写入项目根目录下的".env"文件，文件内容例如:

   ```text
   REDIS_HOST=redis://xxx.xxx.xxx.xxx:6379
   REDIS_CLUSTER_ENABLE=false
   ```

变量列表及说明：

1. 数据库配置

   - DATABASE_URL: 数据库访问参数，例如使用MySQL: mysql://<用户名>:<密码>@<地址>:<端口>/<数据库名称>?charset=utf8mb4
   - DB_CONN_MAX_AGE: 当使用MySQL时，配置连接的最大保持时长

2. Redis配置

   - REDIS_HOST: Redis服务连接参数， 格式：redis://<地址>:<端口>
   - REDIS_CLUSTER_ENABLED: Redis服务是否为集群模式，值为： **true** or **false**
   - REDIS_PREFIX: 为Redis数据Key增加的前缀

3. 学长云配置

   - APP_KEY: 学长云中互动直播服务中创建的应用的Key
   - APP_SECRET: 学长云中互动直播服务中创建的应用的Secret
   - LVB_HOST: 固定值： https://open.jjldxz.com
   
4. 其他配置
   - SALT: 为JWT生成Refresh Token时使用的参数
 
## 数据库初始化

项目第一次运行前，使用Django的标准方式初始化数据库，及创建管理员账户，例如：

```bash
python manage.py migrate

python manage.py makemigrations meeting
python manage.py migrate meeting

python manage.py makemigrations poll
python manage.py migrate poll

python manage.py createsuperuser
```

## 系统运行

### 调试运行

```bash shell
python manage.py runserver 0.0.0.0:8000
```

### 生产运行

```bash shell
daphne -b 0.0.0.0 -p 80 meeting_sample.asgi:application
```

### 打包Docker

```bash shell
poetry export -o requirements.txt --without-hashes # 导出项目依赖
docker build -t meeting_sample:v1 -f ./deployment/Dockerfile .
```

运行Docker镜像

```bash shell
docker run -p 8000:80 --env-file .env meeting_sample:v1
```
