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
            'INCEPTION_HOST': '127.0.0.1',
            'INCEPTION_PORT': 6669,
        },
        'backup': {  # 需要跟 inception 的配置文件中的信息一致，这边用于查找备份
            'BACKUP_USER': 'root',          # inception_remote_system_user=root
            'BACKUP_PASSWORD': '123456',    # inception_remote_system_password=123456
            'BACKUP_PORT': 4901,            # inception_remote_backup_port=4901
            'BACKUP_HOST': '127.0.0.1',     # inception_remote_backup_host=127.0.0.1
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
    [Inception安装文档](http://bac10bd3.wiz03.com/share/s/2WMgLj32GQP92KUCZP2YLIKi0BXq6M3N6QBP2ChQ7O0CHqdo)

    ```
    # C:\Users\Administrator\Miniconda3\envs\AquilaV2\Lib\site-packages\pymysql\connections.py 在 1109 行前面添加如下内容， 只要把第一个点前面改成 大于等于5就行,
    self.server_version = '5.7.18-log'

    # C:\Users\Administrator\Miniconda3\envs\AquilaV2\Lib\site-packages\pymysql\cursors.py 345 行修改如下
    if self._result:
    # if self._result and (self._result.has_next or not self._result.warning_count):
    ```

6. 修改 django models 源码
   这边使用的 conda 下的虚拟环境，路径如下：
   ```
   C:\Users\Administrator\Miniconda3\envs\AquilaV2\Lib\site-packages\django\db\models\fields\__init__.py
   ```
   linux 下默认路径为：
   ```
   /local/lib/python3.5/site-packages/django/db/models/fields/__init__.py
   ```

   __根据5 6 两步给出来的路径信息，路径不同的同学，可以根据其规则来查找自己环境中的源码路径__


   使用下面内容替换原有的内容：
   ```
   __all__ = [str(x) for x in (
        'AutoField', 'BLANK_CHOICE_DASH', 'BigAutoField', 'BigIntegerField',
        'BinaryField', 'BooleanField', 'CharField', 'CommaSeparatedIntegerField',
        'DateField', 'DateTimeField', 'DecimalField', 'DurationField',
        'EmailField', 'Empty', 'Field', 'FieldDoesNotExist', 'FilePathField',
        'FloatField', 'GenericIPAddressField', 'IPAddressField', 'IntegerField',
        'NOT_PROVIDED', 'NullBooleanField', 'PositiveIntegerField',
        'PositiveSmallIntegerField', 'SlugField', 'SmallIntegerField', 'TextField',
        'TimeField', 'URLField', 'UUIDField','TinyIntegerField', 'PositiveTinyIntegerField',
        'PositiveTinyIntAuto', 'PositiveIntegerField', 'PositiveBigIntegerField',
        'SmallTextField', 'PositiveBigIntegerFieldAuto',
    )]
   ```
   在文件最后添加以下内容：
   ```
    # ============================ User Defined Data Type ==============================

    class TinyIntegerField(SmallIntegerField, Field):
        def db_type(self, connection):
            if connection.settings_dict['ENGINE'] == 'django.db.backends.mysql':
                return "tinyint"
            else:
                return super(TinyIntegerField, self).db_type(connection)

    class PositiveTinyIntegerField(PositiveSmallIntegerField, Field):
        def db_type(self, connection):
            if connection.settings_dict['ENGINE'] == 'django.db.backends.mysql':
                return "tinyint UNSIGNED"
            else:
                return super(PositiveTinyIntegerField, self).db_type(connection)


    class PositiveTinyIntAuto(PositiveTinyIntegerField):
        def db_type(self, connection):
            return "tinyint UNSIGNED AUTO_INCREMENT"

    class PositiveBigIntegerFieldAuto(IntegerField):
        def db_type(self, connection):
            return "bigint UNSIGNED AUTO_INCREMENT"


    class PositiveIntegerField(IntegerField):
        def db_type(self, connection):
            return "int UNSIGNED"


    class PositiveBigIntegerField(IntegerField):
        def db_type(self, connection):
            return "bigint UNSIGNED"


    class SmallTextField(TextField):
        def db_type(self, connection):
            return "text"
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
    使用 celery 功能时,需要安装 rabbitmq, 默认安装即可，不需要配置

5. 登录
   ```
   http:aquila_v2_ip/login.html
   ```

初始化时只给了管理账号， 其他用户账号自行注册

已完成功能：
1. 元数据收集及展示，收集页面目前属于临时，后期会改成 c/s 模式
2. SQL 发布与审核
3. 支持查看回滚语句
4. 支持查询 ptosc 语句进度