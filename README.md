# currency_rate_collector
Получение курса валют и аккумулирование в ДБ.

**chromedriver** version = 10.2.0  
**chromium-browser** version = Chromium 86.0.4240.197 Built on Raspbian


[How to run Selenium using Python on Raspberry Pi](https://patrikmojzis.medium.com/how-to-run-selenium-using-python-on-raspberry-pi-d3fe058f011)

### Install Chrome Browser
```bash
sudo apt-get install chromium-browser
```

### Verify browser version
```bash
chromium-browser --version
```

### Load Chromedriver
```bash
https://github.com/electron/electron/tags
```

### Move Chromedriver to:
```bash
/usr/lib/chromium-browser/
```

#### Install Virtual Display
```bash
pip3 install pyvirtualdisplay
```

### Useing Virtualdisplay
```python
from pyvirtualdisplay import Display

display = Display(visible=0, size=(800, 600))
display.start()
.
.
.
display.stop()
```

### Run docker with PostgreSQL server
```bash
docker-compose up
```

### Links
[Download PhantomJS](https://phantomjs.org/download.html)
