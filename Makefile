install:
	python3.6 setup.py install
dist:
	python3.6 setup.py sdist bdist_wheel
test:
	cd G/test/ && python3.6 test.py
