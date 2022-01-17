#!/usr/bin/env python3

from signal_analog.flow import Data, Filter
from signal_analog.charts import TimeSeriesChart
from signal_analog.dashboards import Dashboard, DashboardGroup
from signal_analog.combinators import And

"""
Creating a new Dashboard Group with Dashboards
"""
filters = And(Filter('host', 'learn-signalfx'))

program = Data('cpu.utilization', filter=filters).publish()
cpu_chart = TimeSeriesChart().with_name('CPU').with_program(program)

program = Data('postgres_query_time', rollup='rate', filter=filters).publish()
query_time = TimeSeriesChart().with_name('Query Time').with_program(program)

program = Data('memory.utilization', filter=filters).publish()
memory_chart = TimeSeriesChart().with_name('Memory').with_program(program)

dashboard1 = Dashboard().with_name('Dashboard 1').with_charts(query_time, cpu_chart, memory_chart)

dashboard_group = DashboardGroup() \
    .with_name('Learn Signal Analog') \
    .with_dashboards(dashboard1)

if __name__ == '__main__':
    from signal_analog.cli import CliBuilder

    cli = CliBuilder().with_resources(dashboard_group)\
        .build()
    cli()
