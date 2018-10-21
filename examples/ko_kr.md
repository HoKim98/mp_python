# MP 프로그래밍 예시
1. [수식 표현](#ch1)
    - [사칙연산](#ch1-1)
    - [비교문 (Test)](#ch1-2)
    - [복잡한 수식](#ch1-3)
    - [일회성 정의 (Test)](#ch1-4)
2. [메소드 호출](#ch2)
    - [내장 메소드 호출](#ch2-1)
    - [반복 호출](#ch2-2)
3. [사용자 정의 메소드 호출](#ch3)
    - [수식 불러오기](#ch3-1)
    - [함수 구현하기 (TODO)](#ch3-2)
4. [긴 문자열 변수](#ch4)
    - [문장 형식의 변수명](#ch4-1)
    - [디렉토리 형식의 변수명 (Test)](#ch4-2)
5. [GUI 프로그래밍](#ch5)
    - [실시간으로 그래프 확인하기 (Test)](#ch5-1)
    - [그래프 제어하기](#ch5-2)
6. [SSH를 통한 원격 인터프리터 실행](#ch6)
    - [원격 인터프리터 실행](#ch6-1)
    - [Anaconda와 같은 가상 환경에서 실행하기](#ch6-2)

<a name="ch1"></a>
## 1. 수식 표현
<a name="ch1-1"></a>
### 사칙 연산
연관 파일 : `ch1/add.mp`\
연산은 사칙연산, 비교연산, 행렬연산, 지수연산, 범위연산을 지원합니다.
먼저, 간단한 사칙연산을 구현해봅시다.
```
@ a = 3
@ b = 4
@ c = a + b
@ 
@ _ = print(c)
@ save _

c = 7
```
<a name="ch1-2"></a>
### 비교문 수식
연관 파일 : `ch1/comparison.mp`\
간단한 비교연산을 구현해봅시다.
* 본 연산은 실험중입니다.
```
@ a = 3
@ b = 4
@ c = a < b
@ 
@ _ = print(c)
@ save _

c = True
```
<a name="ch1-3"></a>
### 복잡한 수식
연관 파일 : `ch1/expression.mp`\
복잡한 수식을 간단히 표현할 수 있습니다.
```
@ a = 1
@ b = -2
@ c = 1
@ 
@ D = b ** 2 - 4 * a * c
@ x = (-1 * b - D ** .5) / (2 * a)
@ 
@ _ = print(D, x)
@ save _

D = 0
x = 1.0
```
<a name="ch1-4"></a>
### 일회성 정의
연관 파일 : `ch1/disposable.mp`\
`:=` 연산자는 변수에 값이 이미 할당돼있는 경우, 값을 대입하지 않습니다.
특히, 변수에 해당하는 파일이 존재하면 대입이 이루어지지 않습니다.
다만, 적어도 한번이라도 변수에 다음과 같은 대입을 시도한다면,
`save` 시에 해당 변수의 대입 연산자는 `=`에서 `:=`로 바뀝니다.
* 본 연산은 실험중입니다.
```
@ # a에는 값이 있으므로 대입이 이루어지지 않는다.
@ a = 1
@ a := 2
@ 
@ # b에는 값이 없으므로 대입이 이루어진다.
@ b := 1
@ b = 2
@ 
@ _ = print(a, b)
@ save _

a = 1
b = 2
```

<a name="ch2"></a>
## 2. 메소드 호출
<a name="ch2-1"></a>
### 내장 메소드 호출
연관 파일 : `ch2/method.mp`\
내장 메소드를 호출해봅시다. 현재 `array`, `print`, `max`, `min`이 구현되었습니다.
```
@ # 함수를 가리키는 변수들
@ foo = print
@ goo = foo
@ too = goo
@ 
@ # (3, 4) 크기의 배열을 만들고, 2를 더한다.
@ potato = array(3, 4) + 2
@ # 배열을 파이썬(Python)처럼 인덱싱할 수 있습니다.
@ k = potato(0, 1:3) + 3
@ 
@ # print는 두 개 이상의 변수도 허용됩니다.
@ _ = too(potato, k)
@ save _

potato = [[2. 2. 2. 2.]
 [2. 2. 2. 2.]
 [2. 2. 2. 2.]]
k = [5. 5.]
```
<a name="ch2-2"></a>
### 반복 호출
연관 파일 : `ch2/repeat.mp`\
함수를 여러 번 호출하는 경우, * 연산자를 이용하여 간단하게 반복할 수 있습니다.
```
@ i = 5
@ a = 3.14
@ 
@ foo = print * i
@ _ = foo(a)
@ save _

a = 3.14
a = 3.14
a = 3.14
a = 3.14
a = 3.14
```

<a name="ch3"></a>
## 3. 사용자 정의 메소드 호출
<a name="ch3-1"></a>
### 수식 불러오기
연관 파일 : `ch3/saved.mp`, `ch3/aaa.mp`\
`save` 접두사를 이용하면 변수가 **파일**로 저장됩니다.
덕분에 `MP`를 다시 호출하여 변수를 쉽게 불러올 수 있습니다.
```
# 인터프리터 모드 (aaa.mp 파일 생성)
@ x = 3
@ y = 4
@ aaa = x + y
@ save aaa
```
```
# 생성된 aaa.mp
(aaa=((x=3i64)+(y=4i64)))
```
```
# 인터프리터 모드 (aaa.mp 파일 불러오기)
@ _ = print(aaa)
@ save _

aaa = 7
```
<a name="ch3-2"></a>
### 함수 구현하기
연관 파일 : `ch3/def.mp`\
`def` 메소드를 이용하여 함수(매크로)를 구현할 수 있습니다.
```
@ foo = def(x, y, x + y)
@ aaa = foo(3, 4)
@ _ = print(aaa)
@ save _

aaa = 7
```

<a name="ch4"></a>
## 4. 긴 문자열 변수
<a name="ch4-1"></a>
### 문장 형식의 변수명
연관 파일 : `ch4/string.mp`\
`MP`는 문자열을 지원하지 않습니다. 대신 변수명을 문자열처럼 사용 가능합니다.
문자열에 띄워쓰기와 `'`, `"`, `_`, `^` 등의 특수기호를 허용합니다.
단, 띄워쓰기는 변수명에서 무시됩니다.
```
@ my house = 3
@ my cat's year = 2.9
@ 
@ # my house는 myhouse와 같습니다.
@ _ = print(myhouse, my cat's year)
@ save _

myhouse = 3
mycat'syear = 2.9
```
<a name="ch4-2"></a>
### 디렉토리 형식의 변수명
연관 파일 : `ch4/recursion.mp`\
만약 새로운 디렉토리를 만들고, 그곳에 변수를 저장하고 싶다면,
간단히 `.`을 이용하여 디렉토리 구별이 가능합니다.
디렉토리는 자동으로 만들어지고, 빈 디렉토리는 자동으로 제거됩니다.
* 본 연산은 실험중입니다.
```
@ a.b = 3 + 4
@ save a.b
@ 
@ c = 5
@ from a save c

(a 디렉토리에 b.mp 파일 생성)
(a 디렉토리에 c.mp 파일 생성)
```

<a name="ch5"></a>
## 5. GUI 프로그래밍
<a name="ch5-1"></a>
### 실시간으로 그래프 확인하기
`MP`는 그래프를 중심으로 프로그래밍하기 때문에,
강력한 시각화 도구를 이용하는 것은 유용합니다.
`MPCAD`는 `MP`의 시각화를 돕기 위한 `GUI 개발 환경` 도구입니다.
`MPCAD`는 단순히 그래프 간 관계를 시각화하는 것을 넘어,
누구나 쉽고 간편하게 제어할 수 있도록 도와줄 것입니다.
* 본 기능은 실험중입니다.

![A Image describing `MPCAD`](ch5/mpcad.png)

<a name="ch5-2"></a>
### 그래프 제어하기
* 그래프를 커서를 이용하여 제어하는 부분은 현재 미구현 상태입니다.

<a name="ch6"></a>
## 6. SSH를 통한 원격 인터프리터 실행
<a name="ch6-1"></a>
### 원격 인터프리터 실행
`MP`는 쉘처럼 간편하게 사용하도록 설계되었습니다.
때문에 `SSH`를 이용하여 클라이언트가 서버에서 `MP`를 간편히 실행할 수 있습니다.
더 나아가, 일반적인 쉘처럼 사용할 수 있을 뿐만 아니라,
`RemoteInterpreter` 클래스를 이용하여 파이썬 응용 프로그램을 작성할 수 있습니다.
* 원하는 디렉토리에서 작업을 시작하는 부분은 현재 미구현 상태입니다.
#### 쉘을 통한 실행
```bash
python -m mp.remote [hostname] [user] [-p port] [-d dir_process] [-i interpreter]
Password: [password]
```
#### 파이썬을 통한 실행
```python
from mp import RemoteInterpreter

sess = RemoteInterpreter()
sess.connect('[hostname]', '[user]', '[password]', port)
sess.session()
sess.begin_interactive()
```

<a name="ch6-2"></a>
### Anaconda와 같은 가상 환경에서 실행하기
`Python`은 모듈의 의존성이 중요한 프로그래밍 언어입니다.
때문에 모듈 관리에 집중한 다양한 프로그램들이 있습니다.
대표적으로 `Anaconda`가 있는데, 이들 환경에서 `python`을 실행하기 위해선 조금의 과정이 추가됩니다.
`MP`는 `python` 인터프리터를 직접 지정할 수 있게 하여 문제를 해결하려 합니다.
```python
from mp import RemoteInterpreter

sess = RemoteInterpreter()
sess.connect('[hostname]', '[user]', '[password]', port)
sess.session('[interpreter path]')
sess.begin_interactive()
```
