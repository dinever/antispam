# AntiSpam

[![version](https://img.shields.io/pypi/v/antispam.svg?label=version)](https://pypi.python.org/pypi/antispam/)
[![supported](https://img.shields.io/pypi/pyversions/antispam.svg)](https://pypi.python.org/pypi/antispam/)
[![license](https://img.shields.io/pypi/l/antispam.svg)](https://opensource.org/licenses/MIT)

Bayesian anti-spam classifier written in Python.

PyPI: [pypi.python.org/pypi/antispam](https://pypi.python.org/pypi/antispam)
Docs: [antispam.readthedocs.org](http://antispam.readthedocs.org)

# Installation

```
pip install antispam
```

# Usage

Use the built-in model provided & trained by author:

```python
import antispam

antispam.score("Cheap shoes for sale at DSW shoe store!")
# => 0.9657724517163143

antispam.is_spam("Cheap shoes for sale at DSW shoe store!")
# => True

antispam.score("Hi mark could you please send me a copy of your machine learning homework? thanks")
# => 0.0008064840568731558

antispam.is_spam("Hi mark could you please send me a copy of your machine learning homework? thanks")
# => False

```

Train your own modle:

```python
import antispam

d = antispam.Detector("my_model.dat")

d.train("Super cheap octocats for sale at GitHub.", True)
d.train("Hi John, could you please come to my office by 3pm? Ding", False)

msg1 = "Cheap shoes for sale at DSW shoe store!"
d.score(msg1)
# => 0.9999947825633266

d.is_spam(msg1)
# => True

msg2 = "Hi mark could you please send me a copy of your machine learning homework? thanks"
d.score(msg2)
# => 4.021280114849398e-08

d.is_spam(msg2)
# => False
```

Save your model:

```python
d.save()
```

##License

[MIT Licenses](https://opensource.org/licenses/MIT)

