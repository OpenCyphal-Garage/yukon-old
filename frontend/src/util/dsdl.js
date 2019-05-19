export default function parseDataTypeStringDescriptor (type) {
  const parts = type.split(' ')
  let ret = {}

  if (parts.length === 0 || parts.length > 2) {
    console.log(`Invalid type information: '${type}'`)
  }

  let primitiveType = parts[0]

  if (parts[0] === 'saturated') {
    ret.saturated = true
    primitiveType = parts[1]
  }

  if (primitiveType.includes('[')) {
    ret.array = true
  }

  if (primitiveType.startsWith('uint')) {
    ret.unsigned = true
    ret.primitiveType = 'uint'

    ret.type = 'number'
    ret.step = 1
    ret.min = 0
  }

  if (primitiveType.startsWith('int')) {
    ret.primitiveType = 'int'

    ret.type = 'number'
    ret.step = 1
  }

  if (primitiveType.startsWith('bool')) {
    ret.primitiveType = 'bool'

    if (!ret.array) {
      ret.type = 'checkbox'
      ret.bits = 1
    }
  }

  const firstDigit = type.match(/\d/)
  const indexOfFirstDigit = type.indexOf(firstDigit)

  const indexOfLastDigit = ret.array ? type.indexOf('[') - 1 : type.length - 1
  if (indexOfLastDigit === -2) {
    console.log(`Invalid digits for type: '${type}'`)
  }

  ret.bits = parseInt(type.substring(indexOfFirstDigit, indexOfLastDigit))

  if (ret.array) {
    const indexOfEndBracket = type.indexOf(']') - 1
    if (indexOfEndBracket === -2) {
      console.log(`Invalid array bounds for type: '${type}'`)
    }

    const arrayStringDescriptor = type.substring(indexOfLastDigit, indexOfEndBracket)

    const extraLength = arrayStringDescriptor.startsWith('<=') ? 0 : -1 // assume it starts with '<'

    const operatorToLookFor = extraLength === 0 ? '<=' : '<'
    const arrayLengthStart = arrayStringDescriptor.indexOf(operatorToLookFor)

    ret.length = parseInt(arrayStringDescriptor.substring(arrayLengthStart, arrayStringDescriptor.length))
  }

  return ret
}
