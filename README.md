# Hutils #

Utilities for Python.

## inject.py ##

Dependency injection container.

Usage:

1) Declare dependencies using the @require decorator on each
application's component:

```
@require('config', 'service')
class MyComponent()
    ...
```

2) Inject dependencies through the registry at application's startup:

```
Registry(
    Dependency(DevelopmentConfig(), name='config'),
    Dependency(UserService())
).install()
```

3) Use dependencies:

```
c = MyComponent()
print(c.config)
```

## restclient.py ##

Generic REST API.

Usage:

```
rest = api(<REST_API_URL>)

rest.users.get()
rest.users['some_id'].friends.get()
rest.users.get(username='homer')

rest.users.post(new_user)
rest.users['some_id'].friends.post(new_friend)
```

Encoding/decoding (associate resources to encoders/decoders):

```
rest.users.encode = UserJSONEncoder
rest.users.decode = UserJSONDecoder

rest.users.friends.encode = UserJSONEncoder
rest.users.friends.decode = UserJSONDecoder
```

Error mapping (map HTTP errors to Python exceptions):

```
rest.error_mappings[409] = ResourceAlreadyExistsError
```

## promise.py ##

Map reduce implementation.

Usage:

```
promise = Promise()

promise.add(product, 1, 2)
promise.add(product, 2, 3)

print(promise.result) # blocking call
```

## progressbar.py ##

Progress bar for console.

Usage:

```
progressbar = ProgressBar(100)

for i in range(100):
    progressbar.update(1)
```

## memoize.py ##

Memoization utility.

Usage:

```
@memoized('/tmp/calculate_{hash}')
def calculate(a, b):
    return a + b

print(calculate(1, 2))
print(calculate(1, 2)) # memoized result
```
