# Readme

## 개발자 환경구성 가이드

### 1. 환경 설정 파일 위치

- 모든 설정 파일은 프로젝트의 `/config` 디렉토리 아래에 위치해야 합니다.
- 각 환경별로 다음과 같은 파일명을 사용해야 합니다:
  - 개발환경: `config_dev.yaml`
  - 운영환경: `config_prod.yaml`

### 2. 환경 설정 파일의 구조

환경 설정 파일은 YAML 형식을 사용하며, 다음과 같은 구조를 가집니다:

```bash
mq_server:
  host: [RabbitMQ Server Host]
  port: [RabbitMQ Server Port]
  username: [RabbitMQ Username]
  password: [RabbitMQ Password]
  req_queue_name: [Request Queue Name]
  res_queue_name: [Response Queue Name]

log:
  path: [Log File Path]
```

### 3. 파이썬 가상환경 설정 및 활성화
1. 가상 환경을 생성하세요:

   ```
   python3 -m venv venv
   ```

2. 가상 환경을 활성화하세요:

   - **Linux/Mac**:

     ```
     source venv/bin/activate
     ```

   - **Windows**:

     ```
     .\venv\Scripts\activate
     ```

### 4. python 패키지 설치

1. `requirements.txt` 파일에 있는 패키지를 설치하세요:

   ```
   pip install -r requirements.txt
   ```

### 4. 환경 선택

환경은 `APP_ENV` 환경 변수를 사용하여 선택됩니다. 다음과 같이 설정하세요:

- 개발환경:

  ```bash
  export APP_ENV=dev
  ```

- 운영환경:

  ```bash
  export APP_ENV=prod
  ```

### 5. 코어 서버 실행 및 중지

1. 실행

    ```bash
    python src/main.py
    ```

## 배포 가이드

### 1. python 패키지 내보내기

1.  현재 환경의 패키지 목록을 `requirements.txt` 파일에 저장하려면 다음을 실행하세요:

   ```
   pip freeze > requirements.txt
   ```