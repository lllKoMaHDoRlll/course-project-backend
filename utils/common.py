
def retry_on_exception(retries_bound: int = 5):
    def wrapper(func):
        async def inner():
            retries_count = 0
            while retries_count < retries_bound:
                try:
                    return await func()
                except Exception as e:
                    print(e)
                    retries_count += 1
                    print("retrying... retry number:", retries_count)
                    pass
        return inner
    return wrapper

if __name__ == "__main__":

    @retry_on_exception(3)
    def func(value):
        res = value / 0
    
    func(5)