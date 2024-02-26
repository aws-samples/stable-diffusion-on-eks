export function validateConfig (props: any) {
    var checkResult = true
    props.modelsRuntime.forEach((val: any) => {
        if (!(val.modelFilename)) {
          checkResult = false
          console.log("Validation failed: modelFilename should be a valid filename.")
        }
    })
    return checkResult
}