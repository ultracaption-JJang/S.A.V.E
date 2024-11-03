# S.A.V.E client

## 프로젝트 설명
실시간 객체 탐지 및 이미지 캡셔닝을 통한 음성 안내 서비스의 client 코드입니다.  
해당 코드를 실행하시면 kivy로 작성된 어플리케이션 형태의 서비스가 실행됩니다.

## 환경 설정

이 프로젝트에서는 Conda 가상 환경을 사용합니다. 필요한 패키지 및 종속성 정보는 `environment.yaml` 파일에 정의되어 있습니다.

### 1. 환경 생성

`environment.yaml` 파일을 사용하여 Conda 가상 환경을 생성합니다. 

```bash
conda env create -f environment.yaml
```

### 2. 환경 활성화
아래 명령어로 생성된 환경을 활성화합니다.
```bash
conda activate save
```

### 3. 사용 방법
아래의 명령어로 서비스를 실행시켜볼 수 있습니다.
```bash
python main.py
```

#### main.py
 - python의 모바일 앱 라이브러리인 kivy로 작성된 메인 스크립트입니다.
 - YOLO v11 모델의 inference를 실시간으로 확인할 수 있습니다.
 - clipcap 모델의 infernce의 api 응답을 실시간으로 확인할 수 있습니다.

### 주의사항
- python 3.9 버전에서 작성 되었습니다. 