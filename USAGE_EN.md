# M5PaperS3 Calculator App Usage Guide

This USAGE document explains how to install and use the M5PaperS3 calculator app. This program is provided under the Apache License 2.0.

## Preparation

1. Open [UIFlow2.0](https://flow.m5stack.com/) in your browser
2. Connect your M5PaperS3 device to your computer with a USB cable
3. Put the device in DFU mode (press and hold the reset button while pressing the M mode button)

## Project Import Procedure

1. Click the "+" button in the top right corner of the UIFlow2.0 screen to create a new project
2. Select "M5Paper S3" as the device type
3. Enter a name for the project, such as "Calculator"
4. In the project that opens, right-click on the file list on the left and select "Import File"
5. Upload the following files from this repository:
   - calculator.py
   - boot.py

## Transferring the Program to the Device

1. Click the "Connect" button in the upper right corner of the UIFlow2.0 screen
2. Select M5PaperS3 from the displayed device list and connect
3. Click the "Run" button in the upper right to transfer the program to the device
4. When the transfer is complete, the calculator app will start automatically

## Editing in UIFlow2.0

You can edit the code in UIFlow2.0 in two ways:

### 1. Block Programming Mode

1. Click on the "Blocks" tab at the top of the screen
2. Use the displayed blocks to edit the calculator functions
3. Use blocks in the "UI" category to change button design and layout

### 2. Python Code Mode

1. Click on the "Python" tab at the top of the screen
2. The calculator.py code will be displayed
3. Edit the code as needed

## Customization Tips

### Changing Button Designs

```python
# Example of changing button colors
if key in '0123456789.':
    bg_color = 0x00FFFF  # Change number buttons to cyan
elif key in ['+', '-', '*', '/', '=']:
    bg_color = 0xFF0000  # Change operator buttons to red
else:
    bg_color = 0x00FF00  # Change other buttons to green
```

### Customizing the Display

```python
# Example of customizing the display area
def draw_display_area():
    """Function to draw the display area"""
    # Display title
    M5.Lcd.setTextColor(0x0000FF, WHITE)  # Change to blue
    M5.Lcd.setTextSize(3)  # Larger font size
    M5.Lcd.drawString("Custom Calculator", 10, 10)
    
    # Display area (result display part) - change background color
    M5.Lcd.fillRoundRect(20, 50, 500, 80, 8, 0x000000)  # Black background
    M5.Lcd.drawRoundRect(20, 50, 500, 80, 8, 0x00FF00)  # Green border
```

### Example of Additional Features

```python
# Example of adding memory functions (M+, M-, MR, MC)
memory_value = 0

def memory_function(action):
    global memory_value, display_text
    
    if action == "M+":  # Add to memory
        memory_value += float(display_text)
    elif action == "M-":  # Subtract from memory
        memory_value -= float(display_text)
    elif action == "MR":  # Memory recall
        display_text = str(memory_value)
        update_display()
    elif action == "MC":  # Memory clear
        memory_value = 0
```

## Troubleshooting

1. **If the device is not recognized**:
   - Check that the USB cable is properly connected
   - Restart the device and re-enter DFU mode

2. **If the program does not transfer**:
   - Refresh the browser and reconnect
   - Update the device firmware to the latest version

3. **If the display doesn't update**:
   - Call the `update_display()` function to refresh the screen
   - If touch input doesn't work properly, call `empty_touch_buffer()`

4. **If calculation results are incorrect**:
   - Debug the calculation code (use `print` statements)

## Reference Links

- [M5Stack Official Documentation](https://docs.m5stack.com/)
- [M5PaperS3 Product Page](https://shop.m5stack.com/)
- [MicroPython Official Documentation](https://micropython.org/doc/)
- [Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0)
