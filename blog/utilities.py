# Pagination ###########################################################################################################
class Page(object):
    """
    Page object for display pages
    """

    def __init__(self, item_count, page_index=1, page_size=8):
        """
        Init Pagination by item_count, page_index and page_size.

        >>> p1 = Page(100, 1)
        >>> p1.page_count
        13
        >>> p1.offset
        0
        >>> p1.ceiling
        8
        >>> p2 = Page(90, 9, 10)
        >>> p2.page_count
        9
        >>> p2.offset
        80
        >>> p2.ceiling
        90
        >>> p3 = Page(91, 10, 10)
        >>> p3.page_count
        10
        >>> p3.offset
        90
        >>> p3.ceiling
        91
        """
        self.item_count = item_count
        self.page_index = page_index
        self.page_size = page_size
        self.page_count = int(item_count // page_size) + (1 if item_count % page_size != 0 else 0)
        if item_count == 0:
            self.offset = 0
            self.ceiling = 0
            self.page_index = 1
        elif self.page_index > self.page_count:
            self.page_index = self.page_count
            self.offset = self.page_size * (self.page_index - 1)
            self.ceiling = self.item_count
        elif self.page_index == self.page_count:
            self.offset = self.page_size * (self.page_index - 1)
            self.ceiling = self.item_count
        else:
            self.offset = self.page_size * (self.page_index - 1)
            self.ceiling = self.offset + self.page_size

        self.has_next = self.page_count > self.page_index
        self.has_previous = self.page_index > 1


def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        raise e
    if p < 1:
        p = 1
    return p

