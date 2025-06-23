# M5PaperS3 Calculator App

This project is a calculator application for the M5PaperS3 device. It can be run either in the UIFlow2.0 environment or as a standalone MicroPython application.

## License

This project is provided under the Apache License 2.0. See the `license` file for details.

## Features

- Basic arithmetic operations (addition, subtraction, multiplication, division)
- Square root calculation
- Sign inversion
- Decimal point support
- Backspace function
- Clear function
- Error handling

## Usage

### Running with UIFlow2.0

1. Start UIFlow2.0
2. Connect your M5PaperS3 device
3. Upload the calculator.py and boot.py files to UIFlow2.0
4. Use uiflow.json as the configuration file
5. Transfer the program to your M5PaperS3 device
6. Use the calculator app on the device

### Running as standalone MicroPython

1. Connect your M5PaperS3 device via USB
2. Copy boot.py and calculator.py to the device's root directory
3. Restart the device
4. The calculator app will start automatically

## Button Layout

```text
| 7 | 8 | 9 | / |
| 4 | 5 | 6 | * |
| 1 | 2 | 3 | - |
| 0 | . | = | + |
| C |+/-| < |rt |
```

## Button Functions

- **Number buttons (0-9)**: Input values
- **Operators (+, -, *, /)**: Select operation
- **=**: Execute calculation
- **.**: Input decimal point
- **C**: Clear all
- **+/-**: Invert sign (toggle positive/negative)
- **<**: Backspace (delete one character)
- **rt**: Square root calculation

## System Requirements

- UIFlow2.0 environment or run directly as MicroPython
- Specifically for M5PaperS3 device
- Display has digit limitations. Very large numbers will be shown in scientific notation

## Customization

You can customize the appearance and behavior by modifying the following variables in the code:

- `button_width`, `button_height`: Button size
- `button_gap`: Space between buttons
- `start_x`, `start_y`: Starting position of the keypad
- Background color for each button (`bg_color`)

## Troubleshooting

If the app doesn't work properly on your device, check the following:

1. Check the USB serial log for detailed error information
2. Verify that the error handler is working
3. Make sure you're using the latest version of UIFlow2.0
4. Check if your device's firmware is up to date

## Additional Notes

- The code actively uses garbage collection (GC) for memory optimization
- There is a slight delay in touch detection (for improved stability)
- Error handling is built in, and the system will attempt to recover automatically if problems occur
- The project is based on the latest UIFlow MicroPython documentation, but there may be differences between the documentation and the actual implementation. In such cases, make adjustments for your current environment
