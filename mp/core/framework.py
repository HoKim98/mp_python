import numpy as np


MAP_NUM_TYPE = {
    # bool-type is not supported
    'b': np.bool_,
    'i8': np.uint8,
    'i32': np.int32,
    'i64': np.int64,
    'f16': np.float16,
    'f32': np.float32,
    'f64': np.float64,
}
