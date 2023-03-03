import decimal
from decimal import Decimal
from typing import Union

THREE_DIGITS_AFTER_COMMA = Decimal(0.010)
TWO_DIGITS_AFTER_COMMA = Decimal(0.10)
ONE_DIGIT_AFTER_COMMA = Decimal(1.0)


class MeasurementsRepr:
    alpha = 0.95

    def __init__(self,
                 measured_val: Union[float, Decimal, int, str],
                 abs_err: Union[float, Decimal, int, str]):
        self._measured_val = self._measured_value_quantize(measured_val, self._err_round(abs_err))
        self._abs_err = abs(self._err_round(abs_err))
        self._rel_err = abs(self._rel_err_calc(self._measured_val, self._abs_err))
        self._config = {
            "show_rel_err": False,
            "no_exp": True,
            "only_measured_val": False,
            "only_err": False,
            "change_exp": 0,
            "factor_out_err_exp": False,
        }

        self._factor_out_exp = 0

    def get_config(self):
        return self._config.copy()

    def set_config(self, **display_config):
        for k, v in display_config.items():
            if k in self._config.keys() and v is not None:
                self._config[k] = v

    def latex(self) -> str:
        if self._config["only_measured_val"] and self._config["no_exp"]:
            return f"{self._remove_exp(self._measured_val, self._abs_err)}"
        elif self._config["only_measured_val"]:
            return f"{self._get_mantissa(self._measured_val)} \\cdot 10 ^" \
                + "{" + f"{self._get_exp(self._measured_val)}" + "}"

        if self._config["only_err"] and self._config["no_exp"]:
            return f"{self._remove_exp(self._abs_err)}"
        elif self._config["only_err"]:
            return f"{self._get_mantissa(self._abs_err)} \\cdot 10 ^" \
                + "{" + f"{self._get_exp(self._abs_err)}" + "}"

        if self._config["factor_out_err_exp"]:
            self._factor_out_exp = self._get_exp(self._abs_err)
            self._abs_err = self._err_round(
                (self._abs_err * Decimal(10 ** -self._factor_out_exp))
            )

            self._measured_val = self._measured_value_quantize(
                self._measured_val * Decimal(10 ** -self._factor_out_exp),
                self._abs_err)
        elif self._config["change_exp"] != 0 and self._config["change_exp"] is not None:
            self._factor_out_exp = -self._config["change_exp"]
            self._abs_err = self._err_round(self._abs_err * Decimal(10 ** -self._factor_out_exp))
            self._measured_val = self._measured_value_quantize(
                self._measured_val * Decimal(10 ** -self._factor_out_exp),
                self._abs_err)

        if self._config["no_exp"] and not self._config["show_rel_err"]:
            self._abs_err = self._remove_exp(self._abs_err)
            self._measured_val = self._remove_exp(self._measured_val, self._abs_err)

            return f"{self._measured_val} \\pm {self._abs_err}"

        elif self._config["no_exp"] and self._config["show_rel_err"]:

            return f"({self._remove_exp(self._measured_val, self._abs_err)} \\pm {self._remove_exp(self._abs_err)});\\:" \
                   f"\\varepsilon = {self._get_percentage_repr(self._rel_err)}; \\: \\alpha = {MeasurementsRepr.alpha}"

        elif not self._config["no_exp"] and self._config["show_rel_err"]:

            return f"({self._remove_exp(self._measured_val, self._abs_err)} \\pm {self._remove_exp(self._abs_err)}) " \
                   f"\\cdot 10 ^" + "{" + f"{self._factor_out_exp}" + "};\\:" \
                   f"\\varepsilon = {self._get_percentage_repr(self._rel_err)}; \\: \\alpha = {MeasurementsRepr.alpha}"

        elif not self._config["no_exp"] and not self._config["show_rel_err"]:

            return f"({self._remove_exp(self._measured_val, self._abs_err)} \\pm {self._remove_exp(self._abs_err)}) " \
                   f"\\cdot 10 ^" + "{" + f"{self._factor_out_exp}" + "}"

    def _remove_exp(self, d: Decimal, err: Decimal = None) -> Decimal:
        if err is None:
            err = d
        sci_repr_err = self._exp_repr(err)
        if ".0E" in sci_repr_err and self._get_exp(err) < 1:
            str_integral_err = str(err.quantize(Decimal(1))) if err == err.to_integral() else str(err.normalize())
            if '.' not in str_integral_err:
                str_integral_err += ".0"
            else:
                str_integral_err += '0'
            return d.quantize(Decimal(str_integral_err))
        else:
            return d.quantize(Decimal(1)) if d == d.to_integral() else d.normalize()

    @staticmethod
    def _exp_repr(d: Union[float, Decimal, int, str]) -> str:
        return "{:E}".format(Decimal(d))

    def _err_round(self, err_val: Union[float, Decimal]) -> Decimal:
        if err_val - int(err_val) <= 10 ** -6 and 1 <= int(err_val) <= 3:
            return decimal.Context(prec=2,
                                   rounding=decimal.ROUND_HALF_EVEN).create_decimal(err_val + Decimal(0.0001))
        for _ in range(2):
            first_digit = int(self._exp_repr(abs(err_val))[0])
            rounded_digits = 1 if first_digit >= 4 else 2
            err_val = decimal.Context(prec=rounded_digits,
                                      rounding=decimal.ROUND_HALF_EVEN).create_decimal(float(err_val))

        return err_val

    @staticmethod
    def _measured_value_quantize(measured_val: Union[float, Decimal, int, str],
                                 rounded_err_val: Decimal) -> Decimal:
        measured_val = Decimal(measured_val)
        return measured_val.quantize(rounded_err_val)

    def _rel_err_calc(self,
                      measured_val: Union[float, Decimal, int, str],
                      err_val: Union[float, Decimal, int, str]) -> Decimal:
        return self._err_round(Decimal(err_val) / Decimal(measured_val))

    def _get_percentage_repr(self, d: Decimal, no_exp=True) -> str:
        return f"{self._remove_exp(self._err_round(d * 100))}\\%" if no_exp else f"{self._err_round(d * 100)}\\%"

    def _get_exp(self, value: Decimal) -> int:
        return int(self._exp_repr(value).split("E")[1])

    def _get_mantissa(self, value: Decimal) -> str:
        return self._exp_repr(value).split("E")[0]


if __name__ == '__main__':
    d1 = 426_569.266841
    d2 = -0.00003
    # d2 = decimal.Context(prec=2,
    #                      rounding=decimal.ROUND_HALF_EVEN).create_decimal(1.001).quantize(Decimal('1000000000'))
    m = MeasurementsRepr(d1, d2)
    config = m.get_config()
    config.update(factor_out_err_exp=False, no_exp=True)
    m.set_config(**config)
    print(m.latex())
    # print("{:E}".format(Decimal(d2)))
    # print(d2)
