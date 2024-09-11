publish-test:
	rm -rf build/ dist/
	python -m build
	twine upload -r testpypi dist/*

publish:
	rm -rf build/ dist/
	python -m build
	twine upload dist/*
