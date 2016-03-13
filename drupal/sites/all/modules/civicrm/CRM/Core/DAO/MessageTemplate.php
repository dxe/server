<?php
/*
+--------------------------------------------------------------------+
| CiviCRM version 4.7                                                |
+--------------------------------------------------------------------+
| Copyright CiviCRM LLC (c) 2004-2015                                |
+--------------------------------------------------------------------+
| This file is a part of CiviCRM.                                    |
|                                                                    |
| CiviCRM is free software; you can copy, modify, and distribute it  |
| under the terms of the GNU Affero General Public License           |
| Version 3, 19 November 2007 and the CiviCRM Licensing Exception.   |
|                                                                    |
| CiviCRM is distributed in the hope that it will be useful, but     |
| WITHOUT ANY WARRANTY; without even the implied warranty of         |
| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.               |
| See the GNU Affero General Public License for more details.        |
|                                                                    |
| You should have received a copy of the GNU Affero General Public   |
| License and the CiviCRM Licensing Exception along                  |
| with this program; if not, contact CiviCRM LLC                     |
| at info[AT]civicrm[DOT]org. If you have questions about the        |
| GNU Affero General Public License or the licensing of CiviCRM,     |
| see the CiviCRM license FAQ at http://civicrm.org/licensing        |
+--------------------------------------------------------------------+
*/
/**
 * @package CRM
 * @copyright CiviCRM LLC (c) 2004-2015
 *
 * Generated from xml/schema/CRM/Core/MessageTemplate.xml
 * DO NOT EDIT.  Generated by CRM_Core_CodeGen
 */
require_once 'CRM/Core/DAO.php';
require_once 'CRM/Utils/Type.php';
class CRM_Core_DAO_MessageTemplate extends CRM_Core_DAO
{
  /**
   * static instance to hold the table name
   *
   * @var string
   */
  static $_tableName = 'civicrm_msg_template';
  /**
   * static instance to hold the field values
   *
   * @var array
   */
  static $_fields = null;
  /**
   * static instance to hold the keys used in $_fields for each field.
   *
   * @var array
   */
  static $_fieldKeys = null;
  /**
   * static instance to hold the FK relationships
   *
   * @var string
   */
  static $_links = null;
  /**
   * static instance to hold the values that can
   * be imported
   *
   * @var array
   */
  static $_import = null;
  /**
   * static instance to hold the values that can
   * be exported
   *
   * @var array
   */
  static $_export = null;
  /**
   * static value to see if we should log any modifications to
   * this table in the civicrm_log table
   *
   * @var boolean
   */
  static $_log = false;
  /**
   * Message Template ID
   *
   * @var int unsigned
   */
  public $id;
  /**
   * Descriptive title of message
   *
   * @var string
   */
  public $msg_title;
  /**
   * Subject for email message.
   *
   * @var text
   */
  public $msg_subject;
  /**
   * Text formatted message
   *
   * @var longtext
   */
  public $msg_text;
  /**
   * HTML formatted message
   *
   * @var longtext
   */
  public $msg_html;
  /**
   *
   * @var boolean
   */
  public $is_active;
  /**
   * a pseudo-FK to civicrm_option_value
   *
   * @var int unsigned
   */
  public $workflow_id;
  /**
   * is this the default message template for the workflow referenced by workflow_id?
   *
   * @var boolean
   */
  public $is_default;
  /**
   * is this the reserved message template which we ship for the workflow referenced by workflow_id?
   *
   * @var boolean
   */
  public $is_reserved;
  /**
   * Is this message template used for sms?
   *
   * @var boolean
   */
  public $is_sms;
  /**
   * a pseudo-FK to civicrm_option_value containing PDF Page Format.
   *
   * @var int unsigned
   */
  public $pdf_format_id;
  /**
   * class constructor
   *
   * @return civicrm_msg_template
   */
  function __construct()
  {
    $this->__table = 'civicrm_msg_template';
    parent::__construct();
  }
  /**
   * Returns all the column names of this table
   *
   * @return array
   */
  static function &fields()
  {
    if (!(self::$_fields)) {
      self::$_fields = array(
        'id' => array(
          'name' => 'id',
          'type' => CRM_Utils_Type::T_INT,
          'title' => ts('Message Template ID') ,
          'description' => 'Message Template ID',
          'required' => true,
        ) ,
        'msg_title' => array(
          'name' => 'msg_title',
          'type' => CRM_Utils_Type::T_STRING,
          'title' => ts('Message Template Title') ,
          'description' => 'Descriptive title of message',
          'maxlength' => 255,
          'size' => CRM_Utils_Type::HUGE,
        ) ,
        'msg_subject' => array(
          'name' => 'msg_subject',
          'type' => CRM_Utils_Type::T_TEXT,
          'title' => ts('Message Template Subject') ,
          'description' => 'Subject for email message.',
        ) ,
        'msg_text' => array(
          'name' => 'msg_text',
          'type' => CRM_Utils_Type::T_LONGTEXT,
          'title' => ts('Message Template Text') ,
          'description' => 'Text formatted message',
          'html' => array(
            'type' => 'TextArea',
          ) ,
        ) ,
        'msg_html' => array(
          'name' => 'msg_html',
          'type' => CRM_Utils_Type::T_LONGTEXT,
          'title' => ts('Message Template HTML') ,
          'description' => 'HTML formatted message',
          'html' => array(
            'type' => 'RichTextEditor',
          ) ,
        ) ,
        'is_active' => array(
          'name' => 'is_active',
          'type' => CRM_Utils_Type::T_BOOLEAN,
          'title' => ts('Is Active') ,
          'default' => '1',
        ) ,
        'workflow_id' => array(
          'name' => 'workflow_id',
          'type' => CRM_Utils_Type::T_INT,
          'title' => ts('Message Template Workflow') ,
          'description' => 'a pseudo-FK to civicrm_option_value',
        ) ,
        'is_default' => array(
          'name' => 'is_default',
          'type' => CRM_Utils_Type::T_BOOLEAN,
          'title' => ts('Message Template Is Default?') ,
          'description' => 'is this the default message template for the workflow referenced by workflow_id?',
          'default' => '1',
        ) ,
        'is_reserved' => array(
          'name' => 'is_reserved',
          'type' => CRM_Utils_Type::T_BOOLEAN,
          'title' => ts('Message Template Is Reserved?') ,
          'description' => 'is this the reserved message template which we ship for the workflow referenced by workflow_id?',
        ) ,
        'is_sms' => array(
          'name' => 'is_sms',
          'type' => CRM_Utils_Type::T_BOOLEAN,
          'title' => ts('Message Template is used for SMS?') ,
          'description' => 'Is this message template used for sms?',
        ) ,
        'pdf_format_id' => array(
          'name' => 'pdf_format_id',
          'type' => CRM_Utils_Type::T_INT,
          'title' => ts('Message Template Format') ,
          'description' => 'a pseudo-FK to civicrm_option_value containing PDF Page Format.',
          'pseudoconstant' => array(
            'optionGroupName' => 'pdf_format',
            'keyColumn' => 'id',
            'optionEditPath' => 'civicrm/admin/options/pdf_format',
          )
        ) ,
      );
    }
    return self::$_fields;
  }
  /**
   * Returns an array containing, for each field, the arary key used for that
   * field in self::$_fields.
   *
   * @return array
   */
  static function &fieldKeys()
  {
    if (!(self::$_fieldKeys)) {
      self::$_fieldKeys = array(
        'id' => 'id',
        'msg_title' => 'msg_title',
        'msg_subject' => 'msg_subject',
        'msg_text' => 'msg_text',
        'msg_html' => 'msg_html',
        'is_active' => 'is_active',
        'workflow_id' => 'workflow_id',
        'is_default' => 'is_default',
        'is_reserved' => 'is_reserved',
        'is_sms' => 'is_sms',
        'pdf_format_id' => 'pdf_format_id',
      );
    }
    return self::$_fieldKeys;
  }
  /**
   * Returns the names of this table
   *
   * @return string
   */
  static function getTableName()
  {
    return self::$_tableName;
  }
  /**
   * Returns if this table needs to be logged
   *
   * @return boolean
   */
  function getLog()
  {
    return self::$_log;
  }
  /**
   * Returns the list of fields that can be imported
   *
   * @param bool $prefix
   *
   * @return array
   */
  static function &import($prefix = false)
  {
    if (!(self::$_import)) {
      self::$_import = array();
      $fields = self::fields();
      foreach($fields as $name => $field) {
        if (CRM_Utils_Array::value('import', $field)) {
          if ($prefix) {
            self::$_import['msg_template'] = & $fields[$name];
          } else {
            self::$_import[$name] = & $fields[$name];
          }
        }
      }
    }
    return self::$_import;
  }
  /**
   * Returns the list of fields that can be exported
   *
   * @param bool $prefix
   *
   * @return array
   */
  static function &export($prefix = false)
  {
    if (!(self::$_export)) {
      self::$_export = array();
      $fields = self::fields();
      foreach($fields as $name => $field) {
        if (CRM_Utils_Array::value('export', $field)) {
          if ($prefix) {
            self::$_export['msg_template'] = & $fields[$name];
          } else {
            self::$_export[$name] = & $fields[$name];
          }
        }
      }
    }
    return self::$_export;
  }
}
