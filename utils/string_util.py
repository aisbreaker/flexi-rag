

def str_limit(s: any, max_len: int = 40) -> str:
    if s is None:
        return None
    s = str(s)
    return s if len(s) <= max_len else (s.strip()[:max_len] + (('...['+str(len(s))+']') if len(s) > max_len else ''))
