aquila_v2 为 Aquila 的第二版本，第一版本代码有点乱，所以重写了第二版，更新了大量代码与实现方式



 一、准备工作

1. 修改数据库连接信息，修改aquila_v2下容的 settions.py 文件内
    根据你的实际地址修改
    ```
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'aquila2',
            'USER': 'root',
            'PASSWORD': '123456',
            'HOST': '192.168.1.6',
            'PORT': 3306
        }
    }
    ```

2. 修改 Inception 信息

    修改Aquila下的settions.py 文件内容, 根据你的实际地址修改

    ```
    INCEPTION = {
        'default': {
            'INCEPTION_HOST': '192.168.1.6',
            'INCEPTION_PORT': 6669,
        },
        'backup': {
            'BACKUP_USER': 'root',
            'BACKUP_PASSWORD': '123456',
            'BACKUP_PORT': 3306,
            'BACKUP_HOST': '192.168.1.6',
        },
    }
    ```

3. 修改用户密码加密 KEY, 根据自己爱好设置
    ```
    USER_ENCRYPT_KEY = '3df6a1341e8b'
    ```

4. 创建数据
    根据前面配置信息去对应的数据库里面去创建，我这边是 192.168.1.6 下创建的 aquila2

5. 使用 inception 功能时，需要修改pymysql的源码， 修改如下：
    ```
    # /usr/local/lib/python3.5/site-packages/pymysql/connections.py 在1071 行前面添加如下内容， 只要把第一个点前面改成 大于等于5就行,
    self.server_version = '5.7.18-log'

    # /usr/local/lib/python3.5/site-packages/pymysql/cursors.py 345 行修改如下
    if self._result:
    # if self._result and (self._result.has_next or not self._result.warning_count):
    ```

二、运行环境准备
1. 虚拟环境准备
推荐使用 conda 的虚拟环境来运行 aquila_v2 所需要的 python 环境
[使用总结](http://python.jobbole.com/86236/)
[清华大学开源软件镜像站](https://mirror.tuna.tsinghua.edu.cn/help/anaconda/)
上面的虚拟环境准备好并处于激活状态后，到项目的要目录下执行
    ```
    pip install -r requestment.txt
    ```

2. 创建项目所有需要的表
进入到项目目录执行：
    ```
    python manage.py migrate
    ```
3. 初始化数据

运行 scripts/init_data.py 文件， 默认的管理员账号和密码为: admin/123456

4. 启动 aquila
    ```
    python manage.py runserver 0.0.0.0:8001
    celery -A aquila_v2 worker
    ```

5. 登录
   ```
   http:aquila_v2_ip/login.html
   ```

初始化时只给了管理账号， 其他用户账号自行注册

注意事项：

1. 工单执行时，当前页面不能离开，等到 “任务已经提交到后台执行，请《工单查询》页面查看进度” 出现后，才能刷新页面，不然执行结果不会记录到数据库中，在工单查询页面看到这个工单一直是执行状态， 所以这点得注意下

2. 工单的回滚 和 工单执行进度 目前还没有，后面添加