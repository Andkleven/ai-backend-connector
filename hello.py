


def cursor_up(lines):
    return '\x1b[{0}A'.format(lines)


shared_data = {
        "actualDuration": -1,
        "actualDurationFPS": -1,
        "totalDuration": -1,
        "totalDurationFPS": -1,
        "imageCaptureDuration": -1,
        "obsCreationDuration": -1,
        "brainDuration": -1,
        "frontendDuration": -1,
        "status": "Initialized",
        "lowerObs": [],
        "upperObs": [],
        "angles": []
    }
console_text = f'Status: {shared_data["status"]} \n' + f'Real FPS: \t\t{shared_data["actualDurationFPS"]:4.1f}FPS \n' + f'Real process time: \t{shared_data["actualDuration"]*1000:5.0f}ms\n' + f'Limited FPS: \t\t{shared_data["totalDurationFPS"]:4.1f}FPS \n' + f'Limited process time: \t{shared_data["totalDuration"]*1000:5.0f}ms \n' + f'Image cap dur: \t\t{shared_data["imageCaptureDuration"]*1000:5.0f}ms \n' + f'Obs dur: \t\t{shared_data["obsCreationDuration"]*1000:5.0f}ms \n' + f'Brain dur: \t\t{shared_data["brainDuration"]*1000:5.0f}ms \n' + f'Frontend dur: \t\t{shared_data["frontendDuration"]*1000:5.0f}'
line_jumps = console_text.count('\n')+2
print(console_text)
print(cursor_up(line_jumps))