mkdir -p build
javac src/*.java -d build
cd build

jar cfe ../NistDp3.jar Main *.class

cd ..
echo "Jar file successfully created."
