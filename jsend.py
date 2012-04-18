__author__ = 'ben'


def decompress(s):
    if '==' in s:
        s1, s2 = s.split('==')
    else:
        s1 = s
        s2 = False
    sDataTmp2 = False
    sDataTmp1 = decompressLZW(decodeBinary(decode847(s1)))
    if s2:
        sDataTmp2 = decompressLZW(decodeBinary(decode847(s2)))

    # Regenerate Data
    sData = ''
    aLookup = {
        128: 8364,
        130 : 8218, 131 : 402,  132 : 8222, 133 : 8230, 134 : 8224,
        135 : 8225, 136 : 710,  137 : 8240, 138 : 352,  139 : 8249, 140 : 338,
        142 : 381,  145 : 8216, 146 : 8217, 147 : 8220, 148 : 8221, 149 : 8226,
        150 : 8211, 151 : 8212, 152 : 732,  153 : 8482, 154 : 353,  155 : 8250,
        156 : 339,  158 : 382,  159 : 376
    }

    # Merge strings (only if UTF-8 chars were used)

    if sDataTmp2:
        for i in range(len(sDataTmp1)):
            sTmp1 = sDataTmp1[i]
            sTmp2 = ord(sDataTmp2[i])
            if sTmp2 != 224:
                sData += unichr((ord(sTmp1) + 256 * sTmp2))
            else:
                if ord(sTmp1) > 127:
                    sData += sTmp1.encode('utf-8')
                else:
                    sData += sTmp1
    else:
        sData = sDataTmp1.encode('utf-8')

    for sKey in aLookup:
        iValue = aLookup[sKey]
        sData.replace(chr(194) + chr(sKey), unichr(iValue))
    return sData[1:]

def decode847(sChars):
    iByte = 7
    iMask = 0
    aCharCodes = []
    i = 0
    while i < len(sChars):
        iValue = ord(sChars[i])
        if iValue == 61:
            i+= 1
            iValue = ord(sChars[i]) - 16
        if iByte > 6:
            iMask = iValue
            iByte = 0
        else:
            pt = 2**iByte
            if iMask & pt == pt:
                iValue += 128

            aCharCodes.append(iValue)
            iByte += 1
        i+= 1
    return aCharCodes

def decodeBinary(aCharCodes):
    aCodes = []
    iDictCount = 256
    iBits = 8
    iRest = 0
    iRestLength = 0
    for i in range(len(aCharCodes)):
        iRest = (iRest << 8) + aCharCodes[i]
        iRestLength += 8
        if iRestLength >= iBits:
            iRestLength -= iBits
            aCodes.append(iRest >> iRestLength)
            iRest &= (1 << iRestLength) - 1
            iDictCount+=1
            if iDictCount >> iBits:
                iBits += 1
    return aCodes


def decompressLZW(aCodes):
    print "derp"
    print "aCodes", aCodes
    sData = ''
    oDictionary = [chr(x) for x in range(ord("\x00"), ord("\xff")+1)]
    if type(aCodes) == type([]):
        aDict = {}
        for i in range(len(aCodes)):
            aDict[i] = aCodes[i]
        aCodes = aDict


    for sKey in aCodes:
        iCode = aCodes[sKey]
        try:
            sElement = oDictionary[iCode]
        except IndexError:
            sElement = None
        if not sElement:
            sElement = sWord + sWord[0]
        sData += sElement
        if sKey:
            oDictionary.append(sWord + sElement[0])
        sWord = sElement
    return sData

def unichr(iCode):
    if iCode <= 0x7F:
        return chr(iCode)
    elif iCode <= 0x7FF:
        return chr(0xC0 | iCode >> 6) + chr(0x80 | iCode & 0x3F)
    elif iCode <= 0xFFFF:
        return chr(0xE0 | iCode >> 12) + chr(0x80 | iCode >> 6 & 0x3F) + chr(0x80 | iCode & 0x3F)
    elif iCode <= 0x10FFFF:
        return chr(0xF0 | iCode >> 18) + chr(0x80 | iCode >> 12 & 0x3F
                                    )  + chr(0x80 | iCode >> 6 & 0x3F
                                    )  + chr(0x80 | iCode & 0x3F)
    else:
        return False


