export const CastModes = {
  SATURATED: 'saturated',
  TRUNCATED: 'truncated'
}

export const PrimitiveTypes = {
  BOOL: {
    name: 'bool',
    needsLengthParsing: false
  },
  INTX: {
    name: 'int',
    needsLengthParsing: true
  },
  UINTX: {
    name: 'uint',
    needsLengthParsing: true
  },
  FLOAT16: {
    name: 'float16',
    needsLengthParsing: false
  },
  FLOAT32: {
    name: 'float16',
    needsLengthParsing: false
  },
  FLOAT64: {
    name: 'float16',
    needsLengthParsing: false
  }
}
