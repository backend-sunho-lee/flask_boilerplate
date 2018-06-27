# Flask Boilerplate
> Flask를 사용하면서 계속해서 사용하게 될 부분들을 보일러플레이트로 만들었습니다.



## Architecture
```shell
boilerplate
├─ app
│	└─ modules
├─ configs
├─ requirements.txt
└─ run.py
```




## Configuration

```shell
configs
├── __init__.py
├── cert_key
│   ├── pfx.cert_key.crt
│   └── pfx.cert_key.key
└── google_client_secret.json
```


#### Configuration 설정하기

1. configs/\__init__.py로 이동
2. Config 클래스에 필요한 값들 설정한다.
3. Config 클래스를 ProdConfig, DevConfig, TestConfig에 상속시킨다.
4. 각 환경에 따라 필요한 값으로 설정해준다.


#### Configuration 적용하기

1. 환경변수 `PURPOSE`를 PROD 또는 DEV로 설정한다.
2. app/\__init__.py 에서 `PURPOSE`에 따라 어떤 Config 클래스를 상속받을지 설정한다.

```python
#: Configurations
import configs
# from configs import ProdConfig, DevConfig, Config

if os.environ.get('PURPOSE') == 'PROD':
    app.config.from_object(configs.ProdConfig)
elif os.environ.get('PURPOSE') == 'DEV':
    app.config.from_object(configs.DevConfig)
else:
    app.config.from_object(configs.Config)
```





## Modules

```shell
module
├─ __init__.py	# 폴더를 모듈로써 인식시키려면 반드시 필요
├─ urls.py
├─ controllers.py
	# 입력과 응답 값들만 오가도록, 최대한 간단하게
	# 요청 데이터, 사용자 권한 등 입력된 데이터 검사하는 작업만
└─ models.py
	# 데이터베이스 작업
	# 복잡한 작업은 다 여기서
```


### About Modules

```shell
app
├─ auth
	# 로컬, 페이스북, 구글 로그인 가능
	# 어떤 OAuth를 붙여도 social_callback()을 통하여 일괄 처리하도록 만듦
	# flask_login으로 사용자 세션 관리
├─ module01
    # 모듈을 하나씩 추가하는 방법으로 진행하려 합니다
├─ __init__.py
└─ common.py
	# 여러 모듈에서 쓰이는, 추후에 다른 프로젝트에서도 잘 쓰일 함수를 모아놓는 곳
```
