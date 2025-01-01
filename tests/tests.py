import re

def test_rgb_cleanup():
    """
        rgb color codes looked like:
         rgb(219,30,42,255)
        but now like:
         rgb(219,30,42,255,rgb:0.85882352941176465,0.11764705882352941,0.16470588235294117)
    """
    c = 'rgb(219,30,42,255)'
    #c = 'rgb(219,30,42,255,rgb:0.85882352941176465,0.11764705882352941,0.16470588235294117)'
    #c = '0,0,0,255,rgb:0,0,0,1'
    match1 = re.search(r'rgb\(\d+,\d+,\d+', c)
    match2 = re.search(r'\d+,\d+,\d+', c)
    if match1:
        c = match1.group(0)
        print(c+')')
    elif match2:
        c = match2.group(0)
        print('rgb('+c+')')
    else:
        print('rgb(100,100,100)')