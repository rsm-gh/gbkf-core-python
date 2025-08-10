
Python implementation of the [Generic Binary Keyed Format (*.gbkf)](https://gbkf-format.org).

This implementation is not yet finished.

## remarks
+ Currently, the Reader and Writer classes store all content in RAM. In the future, they will be improved to support disk-based I/O operations for large files.
+ Floats can induce numerical deltas, for example, writing `100.9` will be read as `100.9000015258789`