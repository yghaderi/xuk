:py:mod:`xuk.options.position_builder`
======================================

.. py:module:: xuk.options.position_builder


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   xuk.options.position_builder.OptionParam
   xuk.options.position_builder.UAParam
   xuk.options.position_builder.StParam
   xuk.options.position_builder.PositionBuilder




.. py:class:: OptionParam


   Bases: :py:obj:`TypedDict`

   dict() -> new empty dictionary
   dict(mapping) -> new dictionary initialized from a mapping object's
       (key, value) pairs
   dict(iterable) -> new dictionary initialized as if via:
       d = {}
       for k, v in iterable:
           d[k] = v
   dict(**kwargs) -> new dictionary initialized with the name=value pairs
       in the keyword argument list.  For example:  dict(one=1, two=2)

   .. py:attribute:: k
      :type: int

      

   .. py:attribute:: premium
      :type: int

      

   .. py:attribute:: qty
      :type: int

      


.. py:class:: UAParam


   Bases: :py:obj:`TypedDict`

   dict() -> new empty dictionary
   dict(mapping) -> new dictionary initialized from a mapping object's
       (key, value) pairs
   dict(iterable) -> new dictionary initialized as if via:
       d = {}
       for k, v in iterable:
           d[k] = v
   dict(**kwargs) -> new dictionary initialized with the name=value pairs
       in the keyword argument list.  For example:  dict(one=1, two=2)

   .. py:attribute:: splot_price
      :type: int

      

   .. py:attribute:: qty
      :type: int

      


.. py:class:: StParam


   Bases: :py:obj:`TypedDict`

   dict() -> new empty dictionary
   dict(mapping) -> new dictionary initialized from a mapping object's
       (key, value) pairs
   dict(iterable) -> new dictionary initialized as if via:
       d = {}
       for k, v in iterable:
           d[k] = v
   dict(**kwargs) -> new dictionary initialized with the name=value pairs
       in the keyword argument list.  For example:  dict(one=1, two=2)

   .. py:attribute:: min
      :type: int

      

   .. py:attribute:: max
      :type: int

      

   .. py:attribute:: step
      :type: int

      


.. py:class:: PositionBuilder(long_call: List[OptionParam], short_call: List[OptionParam], long_put: List[OptionParam], short_put: List[OptionParam], long_ua: List[UAParam], short_ua: List[UAParam], st_range: StParam)


   Build any position and get simulate profit.

   :param long_call: List[OptionParam] long call position params e.g. [{'k':22_000, 'premium':2_000, 'qty':2}]
   :param short_call: List[OptionParam] short call position params e.g. [{'k':22_000, 'premium':2_000, 'qty':2}]
   :param long_put: List[OptionParam] long put position params e.g. [{'k':22_000, 'premium':2_000, 'qty':2}]
   :param short_put: List[OptionParam] short put position params e.g. [{'k':22_000, 'premium':2_000, 'qty':2}]
   :param long_ua: List[UAParam] long underlying asset position params e.g. [{'splot_price':18_000, 'qty':1}]
   :param short_ua: List[UAParam] short underlying asset position params e.g. [{'splot_price':18_000, 'qty':1}]
   :param st_range:
                    StParam to create range of price of assets at maturity,
                        e.g. {'min':2000, 'max':5000,'step':10}

   .. py:method:: simulate_profit() -> List[int]

      The simulation of profit for all given position within the specified range.

      :rtype: List[int]

      .. rubric:: Examples

      >>> from xuk.options import PositionBuilder
      >>> positions = {
      ...    "long_call": [],
      ...    "short_call": [
      ...        {"k": 22_000, "premium": 2_000, "qty": 2},
      ...        {"k": 24_000, "premium": 1_000, "qty": 1},
      ...    ],
      ...    "long_put": [],
      ...    "short_put": [],
      ...    "long_ua": [{"spot_price": 20_000, "qty": 3}],
      ...    "short_ua": [],
      ...}
      >>> pb = PositionBuilder(**positions, st_range={"min": 15_000, "max": 30_000, "step": 10})
      >>> print(pb.simulate_profit())
        [-10000, -9970, ...]
           >>>



