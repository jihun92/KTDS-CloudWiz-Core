# Readme

## 개발자 환경구성 가이드

### 1. 환경 설정 파일 위치

- 모든 설정 파일은 프로젝트의 `/config` 디렉토리 아래에 위치해야 합니다.
- 각 환경별로 다음과 같은 파일명을 사용해야 합니다:
  - 개발환경: `config_dev.yaml`
  - 운영환경: `config_prod.yaml`

### 2. 환경 설정 파일의 구조

환경 설정 파일은 YAML 형식을 사용하며, 다음과 같은 구조를 가집니다:

```
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

### 3. Docker 환경 구성

#### Docker 설치

도커가 설치되지 않은 경우 [도커 공식 문서](https://docs.docker.com/get-docker/)를 참조하여 설치하세요.

#### Docker 이미지 빌드

프로젝트 루트 디렉터리에서 다음 명령을 실행하여 Docker 이미지를 빌드합니다:

```
docker build -t iacops .
```

### 4. Docker 컨테이너 실행

빌드가 완료된 후, 다음 명령으로 Docker 컨테이너를 실행합니다:

```
docker run iacops
```

### 5. 환경 선택 (Docker 컨테이너 내부)

환경은 Docker 컨테이너의 `ENV` 지시문을 사용하여 설정됩니다. `Dockerfile`에 다음과 같이 추가하세요:

- 개발환경:

  ```
  ENV APP_ENV=dev
  ```

- 운영환경:

  ```
  ENV APP_ENV=prod
  ```

### 6. 로깅

- 로그 파일은 컨테이너 내부의 `/app/logs` 디렉터리에 저장됩니다.