from pydantic import constr

username_constr = constr(min_length=2, max_length=256, regex=r"[^@!#%$\/:?&=\s]+")
password_constr = constr(min_length=2, max_length=256)
