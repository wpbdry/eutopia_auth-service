# Authentication Service

Handles all authentication for Eutopia Platform

## Installation

`secret.py` should look like:
```python
database_password = 'password'
send_mail_password = 'my secret!'
```
Edit `config.py` to match your settings

Run:
```commandline
$: pip install -r requirements.txt
$: python3 app.py
```

## Mutations

### Register Email
Registers user as user without password.
Generates temporary signup code
and emails it to user
```gql
mutation {
  registerEmail(email: "name@mail.tld") {
    exitcode
    msg
  }
}
```

#### Exit codes

0: Email successfully registered.
Code successfully emailed to user

2: Email entered is not a valid email address.

3: Email already belongs to full user.

4: Email has already been sent a code which is still valid.
User should use that code or request a new one

500: Email has already been sent a code, but it has expired.
User should request a new code

6: Error adding new user to user database.
See msg for more details.

7: Error adding code to pending_signups database.
See msg for more details

8: Error while sending email

### Login
Allows user to login, with either
temporary signup code, or password
```gql
mutation {
  loginUser(
    email: "myemail@me.com",
    code: "938002"
  ) {
    exitcode
    token
    msg
  }
}
```
OR
```gql
mutation {
  loginUser(
    email: "myemail@me.com",
    password: "secret"
  ) {
    exitcode
    token
    msg
  }
}
```

#### Exit codes

0: User successfully logged in. Token returned.

2: Given email address is not associated with
any user. Please sign up first.

3: This mutation should be passed temporary login code
or password, not both.

4: User has already set a password,
but is trying to log in with temporary code.
Please login with password

500: Code provided has expired.
User should request a new code.

6: Incorrect code.

7: User is trying to log in with password
but has never set one.

8: Incorrect password

9: Error adding token to sessions database.
See msg for more information.

### Logout
Receives a token, and logs out user
```gql
mutation {
  logoutUser(token: "JdtOKQDznKQRNRAJYzEw") {
    exitcode
    msg
  }
}
```

#### Exit codes

0: Token found and user logged out successfullly.

2: Token not found

3: Error deleting token from database.
See msg for more details