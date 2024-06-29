

clean:
	rm -rf build dist Unichat.egg-info

test:
	export PYTHONPATH=$PYTHONPATH:'unichat/'
	python -m unittest discover -s tests/unittests


