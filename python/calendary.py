#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import (
    absolute_import,
    division,
    print_function,
    with_statement,
    unicode_literals
)

from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('jedi', './fonts/Starjedi.ttf'))
pdfmetrics.registerFont(TTFont('faces', './fonts/emoticons.ttf'))
pdfmetrics.registerFont(TTFont('elf', './fonts/halfelven.ttf'))

import calendar, collections, datetime, time
from contextlib import contextmanager

from reportlab.lib import pagesizes
from reportlab.pdfgen.canvas import Canvas

# Supporting languages like French should be as simple as editing this
ORDINALS = {
    1: 'st', 2: 'nd', 3: 'rd',
    21: 'st', 22: 'nd', 23: 'rd',
    31: 'st',
    None: 'th'}

# Something to help make code more readable
Font = collections.namedtuple('Font', ['name', 'size'])
Geom = collections.namedtuple('Geom', ['x', 'y', 'width', 'height'])
Size = collections.namedtuple('Size', ['width', 'height'])

@contextmanager
def save_state(canvas):
    """Simple context manager to tidy up saving and restoring canvas state"""
    canvas.saveState()
    yield
    canvas.restoreState()

def add_calendar_page(
    canvas,
    rect,
    datetime_obj,
    cell_cb,
    events,
    first_weekday=calendar.SUNDAY
):
    """Create a one-month pdf calendar, and return the canvas

    @param rect: A C{Geom} or 4-item iterable of floats defining the shape of
        the calendar in points with any margins already applied.
    @param datetime_obj: A Python C{datetime} object specifying the month
        the calendar should represent.
    @param cell_cb: A callback taking (canvas, day, rect, font) as arguments
        which will be called to render each cell.
        (C{day} will be 0 for empty cells.)

    @type canvas: C{reportlab.pdfgen.canvas.Canvas}
    @type rect: C{Geom}
    @type cell_cb: C{function(Canvas, int, Geom, Font)}
    """
    calendar.setfirstweekday(first_weekday)
    cal = calendar.monthcalendar(datetime_obj.year, datetime_obj.month)
    rect = Geom(*rect)

    # set up constants
    scale_factor = min(rect.width, rect.height)
    line_width = scale_factor * 0.0025
    font = Font('Helvetica', scale_factor * 0.028)
    rows = len(cal)

    # Leave room for the stroke width around the outermost cells
    rect = Geom(rect.x + line_width,
                rect.y + line_width,
                rect.width - (line_width * 2),
                rect.height - (line_width * 1.9))
    cellsize = Size(rect.width / 7, rect.height / rows)
    
    headerX = font.size * 1.3
    canvas.setFont('jedi', 20)
    canvas.drawString(20, rect.height+40, calendar.month_name[datetime_obj.month])
    canvas.setFont('jedi', 12)
    for day in ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"):
        canvas.drawString(headerX, 0+15, day)
        headerX = headerX + cellsize.width
    canvas.setFont(*font)

    # now fill in the day numbers and any data
    for row, week in enumerate(cal):
        for col, day in enumerate(week):
            # Give each call to cell_cb a known canvas state
            with save_state(canvas):

                # Set reasonable default drawing parameters
                canvas.setFont(*font)
                canvas.setLineWidth(line_width)


                cell_cb(canvas, day, Geom(
                    x=rect.x + (cellsize.width * col),
                    y=rect.y + ((rows - row) * cellsize.height),
                    width=cellsize.width, height=cellsize.height),
                    font, scale_factor)
                
                event = events.get("%d-%d"% (datetime_obj.month, day), "false")
                
                if event != "false":
                    canvas.setFont('Helvetica',10)
                    if type(event) is str:
                        canvas.drawString(
                            rect.x + (cellsize.width * col)+1,
                            (rect.y + ((rows - row) * cellsize.height))+5-cellsize.height,
                            event
                        )
                    elif type(event) is list:
                        c = 5
                        for e in event:
                            canvas.drawString(
                                rect.x + (cellsize.width * col)+1,
                                (rect.y + ((rows - row) * cellsize.height))+c-cellsize.height,
                                e
                            )
                            c = c + (10)
                        canvas.setFont(*font)
                        
                if day != 0:
                    canvas.rect(
                        rect.x + (cellsize.width * col)+cellsize.width-15, 
                        (rect.y + ((rows - row) * cellsize.height))-cellsize.height,
                        15,
                        15,
                        stroke=1,
                        fill=0
                    )

    # finish this page
    canvas.showPage()
    
    return canvas

def draw_cell(canvas, day, rect, font, scale_factor):
    """Draw a calendar cell with the given characteristics

    @param day: The date in the range 0 to 31.
    @param rect: A Geom(x, y, width, height) tuple defining the shape of the
        cell in points.
    @param scale_factor: A number which can be used to calculate sizes which
        will remain proportional to the size of the entire calendar.
        (Currently the length of the shortest side of the full calendar)

    @type rect: C{Geom}
    @type font: C{Font}
    @type scale_factor: C{float}
    """
    # Skip drawing cells that don't correspond to a date in this month
    if not day:
        return

    margin = Size(font.size * 0.5, font.size * 1.3)

    # Draw the cell border
    canvas.rect(rect.x, rect.y - rect.height, rect.width, rect.height)

    day = str(day)
    ordinal_str = ORDINALS.get(int(day), ORDINALS[None])

    # Draw the number
    text_x = rect.x + margin.width-6
    text_y = rect.y - margin.height+6
    canvas.drawString(text_x, text_y, day)

    # Draw the lifted ordinal number suffix
    canvas.setFont("elf", 10)
        
    number_width = canvas.stringWidth(day, font.name, font.size)
    canvas.drawString(text_x + number_width ,
                      text_y + (margin.height * 0.1) +2,
                      ordinal_str)
    
    canvas.setFont("faces", 10)
    extra = 13
    if int(day) > 9:
        extra = 5
    c = number_width + canvas.stringWidth(ordinal_str, "elf", 10)+extra
    lem = "S"
    for em in ("S", "W", "N", "C", "A", "D", "B"):
        canvas.drawString(text_x + c,
                      text_y + (margin.height * 0.1) +2,
                      em)
        c = c + 2 + canvas.stringWidth(lem, "faces", 10)
        lem = em
    

def generate_pdf(
    datetime_obj,
    size,
    events,
    first_weekday=calendar.SUNDAY
):
    """Helper to apply add_calendar_page to save a ready-to-print file to disk.

    @param datetime_obj: A Python C{datetime} object specifying the month
        the calendar should represent.
    @param outfile: The path to which to write the PDF file.
    @param size: A (width, height) tuple (specified in points) representing
        the target page size.
    """
    size = Size(*size)
    outdir = "calendar-%s" % datetime_obj.year
    Path(outdir).mkdir(exist_ok=True)
    outfile = "%s/%s.pdf" % (outdir, calendar.month_name[datetime_obj.month])
    canvas = Canvas(outfile, size)

    # margins
    wmar, hmar = size.width / 70, size.height / 20
    size = Size(size.width - (2 * wmar), size.height - (2 * hmar))

    add_calendar_page(
        canvas,
        Geom(wmar, hmar, size.width, size.height),
        datetime_obj,
        draw_cell,
        events,
        first_weekday
    ).save()

if __name__ == "__main__":
    
    dt = datetime.datetime.strptime("2026-04", "%Y-%m")

    events = {
        "7-13":   "Our Anniversary",
        "12-25":  ["Caleb's Birthday", "Bob's Birthday"],
    }
    
    generate_pdf(
        dt,
        pagesizes.landscape(pagesizes.A4),
        events
    )
