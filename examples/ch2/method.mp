# 함수를 가리키는 변수들
foo = print
goo = foo
too = goo

# (3, 4) 크기의 배열을 만들고, 2를 더한다.
potato = array(3, 4) + 2
# 배열을 파이썬(Python)처럼 인덱싱할 수 있습니다.
k = potato(0, 1:3) + 3

# print는 두 개 이상의 변수도 허용됩니다.
_ = too(potato, k)
save _
