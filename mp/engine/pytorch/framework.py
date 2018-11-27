import torch


MAP_NUM_TYPE = {
    # bool-type is not supported
    'b': None,
    'i8': torch.uint8,
    'i32': torch.int32,
    'i64': torch.int64,
    'f16': torch.float16,
    'f32': torch.float32,
    'f64': torch.float64,
}


def new_const(toward, device):
    return torch.full((), fill_value=toward.value, device=device,
                      dtype=MAP_NUM_TYPE[toward.num_type])
