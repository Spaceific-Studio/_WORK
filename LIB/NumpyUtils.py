
import numpy as np

def npRemap(inNpArray, minInput, maxInput, minOutput, maxOutput):
    inDtype = inNpArray.dtype
    inNpArray = np.asarray(inNpArray, dtype = np.float64)
    minInput *= 1.
    maxInput *= 1.
    minOutput *= 1.
    maxOutput *= 1.
    inputSpan = maxInput - minInput
    outputSpan = maxOutput - minOutput
    inNpArray -= minInput
    inNpArray /= inputSpan
    inNpArray *= outputSpan
    inNpArray += minOutput
    inNpArray = np.asarray(inNpArray, dtype = inDtype)
    return inNpArray
