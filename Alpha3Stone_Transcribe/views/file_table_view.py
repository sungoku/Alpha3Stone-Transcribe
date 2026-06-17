"""NSTableView for displaying queued audio files."""

import objc
from AppKit import (
    NSView, NSTableView, NSTableColumn, NSScrollView,
    NSTableViewSelectionHighlightStyleRegular,
    NSBezelBorder, NSViewWidthSizable, NSViewHeightSizable,
)
from Foundation import NSMakeRect, NSObject


class TableDataSource(NSObject):
    """Data source for the file table."""

    def initWithController_(self, controller):
        self = objc.super(TableDataSource, self).init()
        if self is None:
            return None
        self.controller = controller
        return self

    def numberOfRowsInTableView_(self, tableView):
        return len(self.controller.file_items)

    def tableView_objectValueForTableColumn_row_(self, tableView, column, row):
        items = self.controller.file_items
        if row >= len(items):
            return ""
        item = items[row]
        col_id = column.identifier()
        if col_id == "filename":
            return item.filename
        elif col_id == "duration":
            return item.duration_display
        elif col_id == "status":
            return item.status_display
        elif col_id == "output":
            if item.output_path:
                return item.output_path.rsplit("/", 1)[-1]
            return ""
        return ""


class FileTableView(NSView):
    """NSScrollView + NSTableView wrapper (no buttons)."""

    def initWithFrame_controller_(self, frame, controller):
        self = objc.super(FileTableView, self).initWithFrame_(frame)
        if self is None:
            return None
        self.controller = controller

        W = frame.size.width
        H = frame.size.height

        scroll = NSScrollView.alloc().initWithFrame_(NSMakeRect(0, 0, W, H))
        scroll.setHasVerticalScroller_(True)
        scroll.setBorderType_(NSBezelBorder)
        scroll.setAutoresizingMask_(NSViewWidthSizable | NSViewHeightSizable)

        self.table = NSTableView.alloc().initWithFrame_(NSMakeRect(0, 0, W, H))
        self.table.setSelectionHighlightStyle_(NSTableViewSelectionHighlightStyleRegular)
        self.table.setUsesAlternatingRowBackgroundColors_(True)

        self.data_source = TableDataSource.alloc().initWithController_(controller)
        self.table.setDataSource_(self.data_source)

        columns = [
            ("filename", "文件名", 250),
            ("duration", "时长", 60),
            ("status", "状态", 70),
            ("output", "输出文件", 130),
        ]
        for col_id, header, width in columns:
            col = NSTableColumn.alloc().initWithIdentifier_(col_id)
            col.headerCell().setStringValue_(header)
            col.setWidth_(width)
            col.setMinWidth_(40)
            self.table.addTableColumn_(col)

        scroll.setDocumentView_(self.table)
        self.addSubview_(scroll)
        self.scroll = scroll

        return self

    def reloadData(self):
        self.table.reloadData()
