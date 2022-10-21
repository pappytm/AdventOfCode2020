import re

f = open('bag_rules.txt')
rules_text = f.read().split('.\n')
f.close()

KEY_BAG = 'shiny gold'
WASTE_RULE_TEXT = ' bags contain |' \
                  ' bags contain no other|' \
                  'no other| ' \
                  'bags, | ' \
                  'bags| ' \
                  'bag, | ' \
                  'bag'


class RuleSet:
    """ Class representation of a given rule set.

    Attributes
    ----------
    _all_colours: Set containing all possible colours covered by the rules

    _child_bag_colours: Dictionary with each parent colour as a key,
    paired with a set of said colour's child colours as a value.

    _child_bag_counts: Dictionary with each parent colour as a key,
    paired with a dictionary of child colours and their counts within the
    parent colour.
    """
    def __init__(self, unprocessed_rules: list) -> None:
        self._all_colours = set()
        self._child_bag_colours = {}
        self._child_bag_counts = {}
        self._rule_processor(unprocessed_rules)
        self._add_sub_colours()

    def _rule_processor(self, rules: list) -> None:
        """Takes text input rules and uses them for RuleSet attributes.

        Populates self._all_colours, self.child_bag_colours and
        self.child_bag_counts on the first iteration over the rules.

        :param rules: String representation of rules. Each line outlining which
        colours and how many of each should be contained in a particular colour.

        :return: None
        """
        child_bag_counts = {}

        # adding top level bag to all colour set
        for line in rules[:-1]:
            line = re.split(WASTE_RULE_TEXT, line)
            line = [colour for colour in line if colour != '']
            self._all_colours.add(line[0])

            if len(line) > 1:
                # Putting bags types inside top level bag
                self._child_bag_colours[line[0]] = \
                    set([colour[2:] for colour in line[1:]])

                # Putting bag count inside top level bag
                child_bag_counts[line[0]] = \
                    {colour[2:]: int(colour[0]) for colour in line[1:]}

            else:
                # Case where top level bag has no children
                self._child_bag_colours[line[0]] = set()
                child_bag_counts[line[0]] = []

            self._child_bag_counts = child_bag_counts

    def _add_sub_colours(self):
        """Populates self._child_bag_colours with child colours for each colour
        in the rule set.

        :return: None
        """
        depth = self.possible_parents_count(KEY_BAG)
        for colour in list(self._all_colours):
            for second_level_colour in list(self._child_bag_colours[colour]):
                for third_level_colour in list(
                        self._child_bag_colours[second_level_colour]):
                    self._child_bag_colours[colour].add(third_level_colour)

        # continue until full nesting depth is reached
        if self.possible_parents_count(KEY_BAG) != depth:
            self._add_sub_colours()

    def possible_parents_count(self, given_colour: str) -> int:
        """ Tallies number of bags which can contain the given colour.
        
        :param given_colour: string representation of the target child colour.
        :return: Integer count of the different bag colours which can contain
        the given colour (directly or through containing other bags which
        contain it). 
        """
        parent_bags = set()
        for colour in list(self._all_colours):
            if given_colour in self._child_bag_colours[colour]:
                parent_bags.add(colour)
        return len(parent_bags)

    def child_count(self, given_colour: str) -> int:
        """Counts all child bags and children of child bags according to rules.

        :param given_colour: String representation of target parent colour.
        :return: Integer count of all bags contained inside given colour.
        """
        total_bags_contained = 0
        if len(self._child_bag_counts[given_colour]) > 0:
            first_layer = [self._child_bag_counts[given_colour][bag_count] for
                           bag_count in self._child_bag_counts[given_colour]]
            total_bags_contained += sum(first_layer)

            # Traverse down the tree until empty bags are found, counting bags
            for sub_bags in self._child_bag_counts[given_colour]:
                total_bags_contained += \
                    self.child_count(sub_bags) * \
                    self._child_bag_counts[given_colour][sub_bags]

        return total_bags_contained


my_rules = RuleSet(rules_text)
print(my_rules.possible_parents_count(KEY_BAG))
print(my_rules.child_count(KEY_BAG))
