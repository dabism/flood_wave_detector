import networkx as nx


class Filtering:
    """
    This class contains filtering functions for the final graph.
    """

    @staticmethod
    def filter_by_gauge(graph: nx.DiGraph, gauge: str) -> nx.DiGraph:
        """
        This function filters out weakly connected components that have the given gauge as a node.

        :param nx.DiGraph graph: graph to be filtered
        :param str gauge: gauge number to be filtered by as a string
        :return nx.DiGraph: graph that contains only components which have gauge as a node
        """

        comps = list(nx.weakly_connected_components(graph))
        edges = graph.edges()
        comps_copy = comps.copy()
        edges = list(edges)

        comps_new = []
        for comp in comps_copy:
            if Filtering.is_gauge_in_comp(gauge=gauge, comp_list=list(comp)):
                comps_new.append(comp)

        nodes_filtered, edges_filtered = Filtering.nodes_and_edges(comps=comps_new, edges=edges)

        g = nx.DiGraph()
        g.add_nodes_from(nodes_filtered)
        g.add_edges_from(edges_filtered)

        return g

    @staticmethod
    def filter_only_in_interval(graph: nx.DiGraph, start_gauge: str, end_gauge: str) -> nx.DiGraph:
        """
        This function filters for an interval of gauges. Each component's intersection with the given interval
        will be displayed.

        :param nx.DiGraph graph: graph to be filtered
        :param str start_gauge: first gauge of the interval as a string
        :param str end_gauge: last gauge of the interval as a string
        :return nx.DiGraph: graph that contains only components that intersect with the interval
        """

        filtered = Filtering.filter_intersecting_with_interval(graph=graph,
                                                               start_gauge=start_gauge,
                                                               end_gauge=end_gauge)

        comps = list(nx.weakly_connected_components(filtered))
        edges = filtered.edges()
        edges = list(edges)

        gauges = Filtering.get_gauges(comps=comps)

        gauges_to_delete = gauges[:gauges.index(start_gauge)]
        comps = Filtering.remove_nodes(comps=comps, gauges_to_delete=gauges_to_delete)

        gauges_to_delete = gauges[gauges.index(end_gauge):]
        comps = Filtering.remove_nodes(comps=comps, gauges_to_delete=gauges_to_delete)

        nodes_filtered, edges_filtered = Filtering.nodes_and_edges(comps=comps, edges=edges)

        g = nx.DiGraph()
        g.add_nodes_from(nodes_filtered)
        g.add_edges_from(edges_filtered)

        return g

    @staticmethod
    def filter_intersecting_with_interval(graph: nx.DiGraph, start_gauge: str, end_gauge: str) -> nx.DiGraph:
        """
        This function filters for an interval of gauges. Any component intersecting with the interval will be displayed,
        otherwise deleted.

        :param nx.DiGraph graph: graph to be filtered
        :param str start_gauge: first gauge of the interval as a string
        :param str end_gauge: last gauge of the interval as a string
        :return nx.DiGraph: graph that contains only components that intersect with the interval
        """

        comps = list(nx.weakly_connected_components(graph))
        edges = graph.edges()
        comps_copy = comps.copy()
        edges = list(edges)

        gauges = Filtering.get_gauges(comps=comps)

        filtered_gauges = gauges[gauges.index(start_gauge):gauges.index(end_gauge) + 1]

        comps_new = []
        for comp in comps_copy:
            list_of_bools = []
            for fg in filtered_gauges:
                x = Filtering.is_gauge_in_comp(gauge=fg, comp_list=list(comp))
                list_of_bools.append(x)

            if any(list_of_bools):
                comps_new.append(comp)

        nodes_filtered, edges_filtered = Filtering.nodes_and_edges(comps=comps_new, edges=edges)

        g = nx.DiGraph()
        g.add_nodes_from(nodes_filtered)
        g.add_edges_from(edges_filtered)

        return g

    @staticmethod
    def get_gauges(comps: list) -> list:
        """
        This function collects the gauges corresponding to a node in the actual graph
        :param list comps: list of components in the graph
        :return list: decreasingly sorted gauge numbers
        """

        for i in range(len(comps)):
            comps[i] = list(comps[i])
        nodes = [item for sublist in comps for item in sublist]

        gauges = []
        for node in nodes:
            if node[0] not in gauges:
                gauges.append(node[0])
        decreasing_gauges = sorted(gauges, key=lambda x: str(float(x)), reverse=True)

        return decreasing_gauges

    @staticmethod
    def remove_nodes(comps: list, gauges_to_delete: list) -> list:
        """
        This function removes nodes corresponding to gauges_to_delete from all components.

        :param list comps: list of components
        :param list gauges_to_delete: list of gauges to delete
        :return list: remaining components
        """

        comps_copy = comps.copy()
        for comp in comps_copy:
            comp_copy = comp.copy()
            for elem in comp_copy:
                if any(gtd == elem[0] for gtd in gauges_to_delete):
                    comps[comps.index(comp)].remove(elem)
        return comps

    @staticmethod
    def filter_by_water_level(graph: nx.DiGraph,
                              gauge: str,
                              positions: dict,
                              node_colors: list,
                              height: str) -> nx.DiGraph:
        """
        This function filters out weakly connected components that have high water level at the given gauge.

        :param nx.DiGraph graph: graph to be filtered
        :param str gauge: gauge number to be filtered by as a string
        :param positions: positions of the graph
        :param node_colors: colors of the nodes of the graph; yellow if the water level is low, red if it's high
        :param str height: level group; either "high" or "low"
        :return nx.DiGraph: graph that contains only components that have high water level at the given gauge
        """

        if height == "high":
            c = "red"
        elif height == "low":
            c = "yellow"
        else:
            raise Exception("Height can be either high or low.")

        comps = list(nx.weakly_connected_components(graph))
        edges = graph.edges()
        comps_copy = comps.copy()
        edges = list(edges)
        for comp in comps_copy:
            comp_list = list(comp)
            i0_list = []
            gauge_in_comp = []
            for i in comp_list:
                i0_list.append(i[0])
                if gauge == i[0]:
                    gauge_in_comp.append(i)

            if not any(gauge == elem for elem in i0_list):
                comps.remove(comp)
            else:
                colors_of_gauge = []
                for elem in gauge_in_comp:
                    idx = list(positions.keys()).index(elem)
                    colors_of_gauge.append(node_colors[idx])

                if not any(c == color for color in colors_of_gauge):
                    comps.remove(comp)

        nodes_filtered, edges_filtered = Filtering.nodes_and_edges(comps=comps, edges=edges)

        g = nx.DiGraph()
        g.add_nodes_from(nodes_filtered)
        g.add_edges_from(edges_filtered)

        return g

    @staticmethod
    def is_gauge_in_comp(gauge: str, comp_list: list) -> bool:
        """
        This function checks whether the weakly connected component comp_list has a node at gauge.

        :param str gauge: given gauge number as a string
        :param list comp_list: given weakly connected component as a list
        :return bool: True if the gauge is in the component, False otherwise
        """

        return any(gauge == elem for elem in [i[0] for i in [list(ele) for ele in comp_list]])

    @staticmethod
    def nodes_and_edges(comps: list, edges: list):
        """
        This function finds and collects the nodes and edges of the filtered graph.

        :param list comps: list of the components
        :param list edges: list of the edges
        :return: list of nodes and list of edges
        """

        for i in range(len(comps)):
            comps[i] = list(comps[i])
        nodes = [item for sublist in comps for item in sublist]

        edges_to_keep = []
        for edge in edges:
            found_in_comp = False
            for comp in comps:
                if edge[0] in comp:
                    found_in_comp = True
                    break
            if found_in_comp:
                edges_to_keep.append(edge)

        return nodes, edges_to_keep
