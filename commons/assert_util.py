# assert的工具类，对yaml里validate的断言进行封装
def get_value_by_path(res, path: str):
    """
    根据路径字符串取值，例如：
    "status_code" -> res.status_code
    "json.token" -> res.json()["token"]
    "json.user.id" -> res.json()["user"]["id"]
    """
    if path == "status_code":
        return res.status_code
    elif path.startswith("json."):
        data = res.json()
        keys = path.replace("json.", "").split(".")
        for k in keys:
            data = data[k]
        return data
    elif path == "text":
        return res.text
    else:
        raise Exception(f"不支持的取值路径：{path}")


def execute_validate(res, validate_list):
    """
    执行yaml里validate断言列表
    validate_list 就是yaml读取出来的 validate: 数组
    """
    if not validate_list:
        return

    for rule in validate_list:
        # rule 是 { "eq": ["json.user.id",1] } 这种字典
        op, expr = list(rule.items())[0]
        path, expect_val = expr[0], expr[1]
        actual_val = get_value_by_path(res, path)

        if op == "eq":
            assert actual_val == expect_val, f"断言eq失败：实际={actual_val}，预期={expect_val}"
        elif op == "ne":
            assert actual_val != expect_val, f"断言ne失败：实际={actual_val}，预期={expect_val}"
        elif op == "gt":
            assert actual_val > expect_val, f"断言gt失败：实际={actual_val}，预期={expect_val}"
        elif op == "lt":
            assert actual_val < expect_val, f"断言lt失败：实际={actual_val}，预期={expect_val}"
        elif op == "contains":
            assert expect_val in actual_val, f"断言contains失败：实际={actual_val}，包含内容={expect_val}"
        elif op == "len_eq":
            assert len(actual_val) == expect_val, f"断言len_eq失败：长度实际={len(actual_val)}，预期={expect_val}"
        else:
            raise Exception(f"不支持的断言操作符：{op}")
