# given an array of duplicates return the one that has the most frequency

input = [1, 2, 2, 3, 4,5, 6, 6, 6]


def repeated(input: []) -> int|None: 
  if len(input)==0: 
    return None
  
  d = dict(default  = 0 )
  
  for n in input: 
    if n in d:
      d[n] += 1
    else: 
      d[n] = 1  
    # d[n] += 1

  max = input[0]
  print(max)

  for n in d: 
    if d[n] > d[max]: 
      max = n
      print(max)
  
  return max 


print(repeated(input))


      
