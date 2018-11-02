# 기계 의사코드 (MP)
**기계 의사코드 (MP)** 는 딥러닝 알고리즘을 기술하는 데에 최적화된 오픈 소스 프로그래밍 언어입니다. 
기계 의사코드는 파이썬(Python)의 표현법에 함수형 성질을 강화하여 유연한 모델 표현이 가능합니다.
또한 변수 간의 관계를 그래프로 저장하여, 다른 플랫폼 (
[Tensorflow](https://github.com/tensorflow/tensorflow),
[PyTorch](https://github.com/pytorch/pytorch),
...)에서 활용하기 용이합니다.
무엇보다 변수(메소드)와 파일 간에 일대일 관계가 성립하는 '**파일 기반 프로그래밍 언어**'입니다.
파일은 코드를 관리하기 쉽게 할 뿐만 아니라, 다른 사람들에게 쉽게 배포하도록 도와줍니다.
\
\
**MP**는 본래 딥러닝 관련한 논문들의 알고리즘을 보다 쉽게 기술하기 위해서 고안되었습니다.
MP는 의사코드만큼 기술하기 자유로우나, 의사코드와 달리 실제 실행이 가능합니다.

**MP**는 문자형과 문자열 데이터 타입을 지원하지 않습니다.
이는 딥러닝 모델을 기술하는 데에 불필요하기 때문입니다.

현재 **MP**는 파이썬(Python)으로 `MP 인터프리터`와 `Mp Python-Plan`을 개발중이고,
그래프를 실행하기 위한 `MP Plans`는 다양한 플랫폼을 지원할 예정입니다.

## 업데이트 사항
업데이트에 대한 정보는 다음의 문서를 참고하십시오 :
[kr](https://github.com/kerryeon/mp/blob/master/docs/update/ko_kr.md)

## MP 설치하기 (Python)
파이썬이 설치되어 있다면, 다음의 순서대로 명령어를 입력해주세요.
```bash
$ pip install mp==0.2.1.2
```
설치가 제대로 되었는지 확인하려면, 다음의 순서대로 명령어를 입력해주세요.
```bash
$ python -c "import mp; print(mp.__version__)"
```
인터프리터에 진입하려면, 빈 디렉토리에 진입하여 다음의 순서대로 명령어를 입력해주세요.
```bash
$ python -m mp.console
```
`MP 인터프리터` 환경에서 다음과 같은 재미있는 코드를 작성해보세요.
다음의 코드가 `y.mp` 파일로 어떻게 정리되는 지 확인해보세요.
```
@ y = x + 3
@ x = 2
@ save y
```

## Build MP
다음의 명령어를 통해 시험 버전의 설치가 가능합니다.
```bash
$ git clone https://github.com/kerryeon/mp
$ cd mp
$ python setup.py install
```

## GUI 프로그래밍
    * 본 기능은 Windows 환경에서 실험중입니다.
### 1. 설치
* 시험 버전을 설치하여 `mp_gui`를 다운로드합니다.
* Windows : 별도의 추가 과정이 필요합니다.
    1. graphviz 모듈이 설치된 디렉토리를 찾습니다.
    2. `envs.txt` 파일의 다음 경로를 자신의 설치 경로에 맞게 수정합니다.
    ```
    'C:/Program Files (x86)/Graphviz2.38/bin'
    ```
### 2. 실행
다음의 명령어를 통해 GUI 프로그램을 실행할 수 있습니다.
```bash
    $ python -m mp_gui.debug
```

## 지원 환경
| **운영 체제**          | **공식 지원 여부** |  **GUI 지원 여부**  | **향후 지원 여부** | **빌드 가능성** |
|:---------------------:|:------------------:|:------------------:|:-----------------:|:--------------:|
| **Linux (Python)**    | *                  |                    | *                 | *              |
| **Windows (Python)**  |                    | *                  | *                 | *              |
| **Mac (Python)**      |                    |                    | *                 | *              |

## 향후계획 (TODO)
* [x] 사용자 정의 메소드 (테스트중)
* [x] 반복문 (테스트중)
* [ ] 역전파
* [ ] GUI 기반 그래프 프로그래밍
* [ ] `PyTorch` 인터프리터 구현
* [ ] `Markdown` 문서 자동화

## 라이선스
[MIT License](https://github.com/kerryeon/mp/blob/master/LICENSE)
