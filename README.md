# Project Structure



## Setup instructions

### Hardware
- Grideye AMG8833

### Install necessary packages 
```python
pip install -r requirements.txt
```

### Tests

#### Pytest

[Good Practices on PyTest](https://docs.pytest.org/en/latest/goodpractices.html)

```python3
pytest --pyargs grideye
```

#### Grideye

> For Ubuntu WSL users, please [install XMING X server](https://sourceforge.net/projects/xming/) and run `export DISPLAY=:0` for the matplotlib visualization to work.

Refer to `testplot.py` for initializing a heatmap and updating its values as output values are received using the functions in `visualizer.py`.

![](screenshots/grideye_heatmap2.gif)
