# 두 수의 곱
mul = def(mul_x, mul_y, mul_x * mul_y)

# 피드백 구조를 구축합니다.
pow_z = (mul * pow_y)(pow_x, 1)
pow = def(pow_x, pow_y, pow_z)

# 실험값
a = mul(3, 5)
b = pow(3, 5)
print a, b
