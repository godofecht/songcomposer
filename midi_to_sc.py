from mido import MidiFile

def midi_to_sc_format(midi_file_path, lyrics, ticks_per_bar=480):
    """
    Converts MIDI data into a custom SC format representing lyric-melody pairs.
    Each line corresponds to one bar containing lyrics followed by notes and their duration tokens.
    
    Args:
        midi_file_path (str): Path to the MIDI file.
        lyrics (list): List of lyric strings for each melody line.
        ticks_per_bar (int): Number of ticks per bar (default is 480).
    
    Returns:
        str: Formatted lyric-melody pairs in the required SC format, with one line per bar.
    """

    def midi_note_to_name(midi_number):
        """
        Converts a MIDI note number to its corresponding note name (e.g., 60 -> C4).
        
        Args:
            midi_number (int): MIDI note number.
        
        Returns:
            str: Corresponding note name.
        """
        note_names = {
            60: "C4", 61: "C#4", 62: "D4", 63: "D#4", 64: "E4", 65: "F4", 66: "F#4", 67: "G4",
            68: "G#4", 69: "A4", 70: "A#4", 71: "B4", 72: "C5", 73: "C#5", 74: "D5", 75: "D#5",
            76: "E5", 77: "F5", 78: "F#5", 79: "G5", 80: "G#5", 81: "A5", 82: "A#5", 83: "B5",
            84: "C6", 85: "C#6", 86: "D6", 87: "D#6", 88: "E6", 89: "F6", 90: "F#6", 91: "G6"
        }
        return note_names.get(midi_number, "Unknown")

    def convert_ticks_to_duration(ticks):
        """
        Converts MIDI ticks to a duration token.
        
        Args:
            ticks (int): Number of ticks representing the note's duration.
        
        Returns:
            int: Duration token corresponding to the number of ticks.
        """
        if ticks < 10:
            return 79  # Representing nearly zero duration
        elif ticks > 500:
            return 512  # Representing long duration (approx 6 seconds)
        return int(ticks / 10)  # Scaling ticks to duration token

    # Read the MIDI file
    midi = MidiFile(midi_file_path)
    prev_time = 0
    current_bar_notes = []
    bars = []

    # Process each track in the MIDI file
    for track in midi.tracks:
        for msg in track:
            if msg.type == 'note_on' and msg.velocity > 0:
                # Convert MIDI note number to note name and calculate duration
                note_name = midi_note_to_name(msg.note)
                duration = convert_ticks_to_duration(msg.time - prev_time)
                note_duration = f"<{note_name}>,<{duration}>"
                current_bar_notes.append(note_duration)

                # Check if the accumulated time exceeds a bar's duration
                if msg.time >= ticks_per_bar:
                    bars.append(current_bar_notes)
                    current_bar_notes = []  # Start a new bar

            prev_time = msg.time
        
        # Append any remaining notes as the final bar
        if current_bar_notes:
            bars.append(current_bar_notes)
    
    # Construct the SC format result
    result = f"Total {len(bars)} lines.\n"
    for i, bar in enumerate(bars):
        # Join the notes in the current bar into a string
        line = " | ".join(bar)
        
        # Add lyrics if available, otherwise skip
        if lyrics:
            lyric_line = lyrics.pop(0)
            result += f"The {['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh'][i]} line: {lyric_line}, {line},\n"
        else:
            result += f"The {['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh'][i]} line: {line},\n"
    
    return result
