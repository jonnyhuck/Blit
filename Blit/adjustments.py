import sympy

def threshold(red_value, green_value=None, blue_value=None):
    """
    """
    if green_value is None or blue_value is None:
        # if there aren't three provided, use the one
        green_value, blue_value = red_value, red_value

    # knowns are given in 0-255 range, need to be converted to floats
    red_value, green_value, blue_value = red_value / 255.0, green_value / 255.0, blue_value / 255.0
    
    def adjustfunc(rgba):
        red, green, blue, alpha = rgba
        
        red[red > red_value] = 1
        red[red <= red_value] = 0
        
        green[green > green_value] = 1
        green[green <= green_value] = 0
        
        blue[blue > blue_value] = 1
        blue[blue <= blue_value] = 0
        
        return red, green, blue, alpha
    
    return adjustfunc

def curves(rgba, black_grey_white):
    """ Adjustment inspired by Photoshop "Curves" feature.
    
        Arguments are three integers that are intended to be mapped to black,
        grey, and white outputs. Curves2 offers more flexibility, see
        curves2().
        
        Darken a light image by pushing light grey to 50% grey, 0xCC to 0x80:
    
          [
            "curves",
            [0, 204, 255]
          ]
    """
    # channels
    red, green, blue, alpha = rgba
    black, grey, white = black_grey_white
    
    # coefficients
    a, b, c = [sympy.Symbol(n) for n in 'abc']
    
    # knowns are given in 0-255 range, need to be converted to floats
    black, grey, white = black / 255.0, grey / 255.0, white / 255.0
    
    # black, gray, white
    eqs = [a * black**2 + b * black + c - 0.0,
           a *  grey**2 + b *  grey + c - 0.5,
           a * white**2 + b * white + c - 1.0]
    
    co = sympy.solve(eqs, a, b, c)
    
    # arrays for each coefficient
    a, b, c = [float(co[n]) * numpy.ones(red.shape, numpy.float32) for n in (a, b, c)]
    
    # arithmetic
    red   = numpy.clip(a * red**2   + b * red   + c, 0, 1)
    green = numpy.clip(a * green**2 + b * green + c, 0, 1)
    blue  = numpy.clip(a * blue**2  + b * blue  + c, 0, 1)
    
    return red, green, blue, alpha

def curves2(rgba, map_red, map_green=None, map_blue=None):
    """ Adjustment inspired by Photoshop "Curves" feature.
    
        Arguments are given in the form of three value mappings, typically
        mapping black, grey and white input and output values. One argument
        indicates an effect applicable to all channels, three arguments apply
        effects to each channel separately.
    
        Simple monochrome inversion:
    
          [
            "curves2",
            [[0, 255], [128, 128], [255, 0]]
          ]
    
        Darken a light image by pushing light grey down by 50%, 0x99 to 0x66:
    
          [
            "curves2",
            [[0, 255], [153, 102], [255, 0]]
          ]
    
        Shaded hills, with Imhof-style purple-blue shadows and warm highlights: 
        
          [
            "curves2",
            [[0, 22], [128, 128], [255, 255]],
            [[0, 29], [128, 128], [255, 255]],
            [[0, 65], [128, 128], [255, 228]]
          ]
    """
    if map_green is None or map_blue is None:
        # if there aren't three provided, use the one
        map_green, map_blue = map_red, map_red

    # channels
    red, green, blue, alpha = rgba
    out = []
    
    for (chan, input) in ((red, map_red), (green, map_green), (blue, map_blue)):
        # coefficients
        a, b, c = [sympy.Symbol(n) for n in 'abc']
        
        # parameters given in 0-255 range, need to be converted to floats
        (in_1, out_1), (in_2, out_2), (in_3, out_3) \
            = [(in_ / 255.0, out_ / 255.0) for (in_, out_) in input]
        
        # quadratic function
        eqs = [a * in_1**2 + b * in_1 + c - out_1,
               a * in_2**2 + b * in_2 + c - out_2,
               a * in_3**2 + b * in_3 + c - out_3]
        
        co = sympy.solve(eqs, a, b, c)
        
        # arrays for each coefficient
        a, b, c = [float(co[n]) * numpy.ones(chan.shape, numpy.float32) for n in (a, b, c)]
        
        # arithmetic
        out.append(numpy.clip(a * chan**2 + b * chan + c, 0, 1))
    
    return out + [alpha]
