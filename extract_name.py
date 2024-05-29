def extract_tokens(input_string):
  commonPart = "INR21700_M50T_T23_Aging_UDDS_SOC20_80_CC"

  tokens = input_string.split('_')

  position = 8
  key1 = ""
  while(not(tokens[position].startswith("N"))):
    key1 = key1 + "_" + tokens[position]
    position = position + 1

  key2 = "_" + tokens[position]
  position = position + 1

  key3 = "_" + tokens[position]
  position = position + 1

  key4 = ""
  if (not(tokens[position].startswith("C"))):
    key4 = tokens[position]
    position = position + 1

  sheetName = tokens[position] + "_" + tokens[position + 1]

  tokens = sheetName.split('.')
  sheetName = tokens[0] + "_1"
  fileName = commonPart + key1 + key2 + key3 + key4 + "_" + tokens[0] + "."
  return fileName, sheetName