remove:
	echo "Removing build dist main.spec"
	rm -rf build dist main.spec
build:remove
	echo "Build is starting"
	pyinstaller --onefile ./src/main.py